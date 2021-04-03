import base64
import sqlite3
import win32crypt
import os
import json
import requests
import hibpwned
import time
import threading

from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt
from PySide2.QtWidgets import QTableWidgetItem
from Cryptodome.Cipher import AES
from shutil import copy

have_i_been_pwned_api = (os.environ["pwned_api_key"])
# Where we will store the collected passwords...
passwords_holder = {"errors":[], "values":[]}
temporary_password_holder = []
emails_gathered = []
# Where we will store results collected from scraping, collecting, matching, etc...
results_holder = {
	"same_passwords":
	{
		"amount": 0,
		"common_passwords":[]
	},
	"weak_passwords":
	{
		"amount": 0, 
		"what_passwords_are_weak":[]
	},
	"leaked_passwords":
	{
		"amount": 0,
		"whats_leaked_or_found":[]
	}
}


def PlaceDataIntoTable(master, table):
	if (table == "pswds"):
		#{"url":url_stored, "username":username_stored, "password":password_stored})
		for i,v in enumerate(results_holder["weak_passwords"]["what_passwords_are_weak"]):
			master.weak_passwords_table.insertRow(i)
			count = 0
			for data in v.values():
				item = QTableWidgetItem("*" * len(data))
				item.setTextAlignment(Qt.AlignCenter)
				master.weak_passwords_table.setItem(i, count, item)
				count += 1
		for x,y in enumerate(results_holder["same_passwords"]["common_passwords"]):
			master.reacurring_passwords_table.insertRow(x)
			count = 0
			for data_rp in y.values():
				item_rp = QTableWidgetItem("*" * len(data_rp))
				item_rp.setTextAlignment(Qt.AlignCenter)
				master.reacurring_passwords_table.setItem(x, count, item_rp)
				count += 1
	elif (table == "pwned_data"):
		for index, value in enumerate(results_holder["leaked_passwords"]["whats_leaked_or_found"]):
			master.summary_table.insertRow(index)
			email, last, amount = QTableWidgetItem('*' * len(value[0].split('@')[0]) + '@' + value[0].split('@')[1]), QTableWidgetItem("*" * len(value[1])), QTableWidgetItem("*" * len(value[2]))

			email.setTextAlignment(Qt.AlignCenter)
			last.setTextAlignment(Qt.AlignCenter)
			amount.setTextAlignment(Qt.AlignCenter)

			master.summary_table.setItem(index, 0, email)
			master.summary_table.setItem(index, 1, last)
			master.summary_table.setItem(index, 2, amount)


def IsPasswordStrongEnough(password):
	"""
	How scores work...

	I believe a solid password should at least has a score of minimum of 3
	We have 5 different points in this function
		1. Password contains upper case
		2. Password contains lower case
		3. Password contains digits
		4. Password contains special characters
		5. Password is longer than 6 characters
	"""

	score = 0
	special_case_letters = ['@', '_', "'", '!', '#', '$', '%', '^', '&', '*', '(', ')', '<', '>', '?', '/', '\\', '|', '}', '{', '~', ':"']

	# check for uppercase 
	if any(x.isupper() for x in password):
		score += 1
	if any(y.islower() for y in password):
		score += 1
	if any(z.isdigit() for z in password):
		score += 1
	if any(special_case_letters in password for special_case_letters in special_case_letters):
		score += 1
	if (len(password) > 6):
		score += 1
	return score


results_holder_shortcut = results_holder["same_passwords"]
class ScrapingFunctions:
	def __init__(self, master):
		self.master = master
	def HaveIBeenPwned(self):
		# This will scrape the data and get the data required
		self.master.console.append("> Starting ScrapingFunctions...")

		count = 1
		self.master.leaked_pass_amount.setText("loading...")
		how_many_emails = (str(len(emails_gathered)))
		self.master.emails_checked_label.setText(f"0 / {how_many_emails} Emails Checked")
		for index, email in enumerate(emails_gathered):
			while True:
				self.master.console.append(f"> Scraping data for this email: {'*' * len(email.split('@')[0]) + '@' + email.split('@')[1]}")
				try:
					self.master.emails_checked_label.setText(f"{index} / {how_many_emails} Emails Checked")
					pwned_request = hibpwned.Pwned(email, 'password ch3ecker', have_i_been_pwned_api)
					myBreaches = pwned_request.searchAllBreaches()
					list_of_sites = []
					if (myBreaches == 404):
						break
					for site in myBreaches:
						if (site == ''):
							continue
						list_of_sites.append(site['Domain'])
						count += 1
					results_holder["leaked_passwords"]["amount"] += len(myBreaches)
					# append email and what has been breached
					results_holder["leaked_passwords"]["whats_leaked_or_found"].append([email, myBreaches[-1]['BreachDate'], list_of_sites])
					
					break
				except Exception as e:
					self.master.emails_checked_label.setText(f"{index} / {how_many_emails} Emails Checked")

					# for avoid being rate limited.
					time.sleep(5)
		self.master.console.append(f"> Finished scraping data ({str(count)} leaked passwords), appending to table...")
		threading.Thread(target=PlaceDataIntoTable, args=(self.master, "pwned_data",), daemon = False).start()
		self.master.leaked_pass_amount.setText(str(count))
		self.master.console.append("> Finished all functions!")

		

	def FilterPasswords(self):
		self.master.console.append("> Starting FilterPasswords function...")

		self.master.recurring_pass_amount.setText("loading...")
		self.master.weak_pass_amount.setText("loading...")
		count_pswds = str(len(passwords_holder["values"]))
		for index, password in enumerate(passwords_holder["values"]):
			url_stored = password[0]
			username_stored = password[1]
			password_stored = password[2]
			if (password_stored in temporary_password_holder):
				results_holder_shortcut["amount"] += 1
				results_holder_shortcut["common_passwords"].append({"username":username_stored, "url":url_stored, "password":password_stored})
			else:
				temporary_password_holder.append(password_stored)

			# Grab weak passwords here
			if (IsPasswordStrongEnough(password_stored) < 3):
				results_holder["weak_passwords"]["amount"] += 1
				results_holder["weak_passwords"]["what_passwords_are_weak"].append({"username":username_stored,"url":url_stored, "password":password_stored})

			self.master.amount_of_pswds_checked.setText(str(f"{index} / {count_pswds} Passwords Checked"))
			time.sleep(0.1)
		self.master.recurring_pass_amount.setText(str(results_holder_shortcut["amount"]))
		self.master.weak_pass_amount.setText(str(results_holder["weak_passwords"]["amount"]))

		self.master.console.append("> Finished FilterPasswords function, now appending to table...")

		threading.Thread(target=PlaceDataIntoTable, args=(self.master, "pswds", ), daemon = False).start()

class FirefoxFunctions:
	def __init__(self):
		pass

class EdgeFunctions:
	def __init__(self):
		pass

class GetAllBrowsers():
	"""
	This will be the main entry for this program.
	It will be executed when the program requires it to fetch data.

	It will execute the Chrome functions, Firefox, edge, etc and grab the required data to start.

	"""
	def __init__(self, master):
		self.master = master
		self.DecryptChrome()
		# Decrypt Firefox here...
		# Decrypt Edge here...
	def DecryptChrome(self):
		ChromeFunctions(master = self.master)


class ChromeFunctions:
	"""
	This module will do all google chrome's functions.
	That including:
		1. Decrypting google chrome saved passwords.

	"""
	def __init__(self, master):
		# self.key will hold the decryption key for the passwords
		self.key = self.decrypt_key()
		self.master = master
		self.grab_passwords()
	def decrypt_key(self):
		# Encrypted_key is the value google uses to encrypt the local saved passwords.
		with open(os.getenv("APPDATA") + "/../Local/Google/Chrome/User Data/Local State", 'r') as file:
			encrypted_key = json.loads(file.read())['os_crypt']['encrypted_key']
			file.close()
		encrypted_key = base64.b64decode(encrypted_key)[5:]
		return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
	def decrypt_string(self, encrypted_value):
		# create cipher object
		cipher = AES.new(self.key, AES.MODE_GCM, nonce=encrypted_value[3:3+12])
		try:
			# refrence: https://superuser.com/questions/146742/how-does-google-chrome-store-passwords
			# Google chrome new way of encrypting their values.
			return cipher.decrypt_and_verify(encrypted_value[3+12:-16], encrypted_value[-16:]).decode()
		except:
			# old way of encryption according to a google article 
			return (win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1]).decode()
	def copy_file(self, path, name):
		# We'll have to copy the sqlite file to another location incase google chrome is currently open
		userhome = os.path.expanduser('~')
		self.destination = ("C:\\Windows\\Temp")
		filePath = os.path.normpath(os.path.join(
			userhome, path))
		try:
			copy(filePath, self.destination+f"\\{name}")
		except Exception as e:
			print(e)
			return False
	def grab_passwords(self):
		# copy the database file
		if(self.copy_file('AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data', 'saved_passwords_copy') == False):
			return False
		self.master.console.append("> Found Google Chrome, decrypting passwords...")

		connect = sqlite3.connect(self.destination+"\\saved_passwords_copy")
		cursor = connect.cursor()
		sql_command = "select action_url, username_value, password_value from logins"
		cursor.execute(sql_command)
		count = 0

		
		for url, username, password in cursor.fetchall():
			try:
				password = self.decrypt_string(password)
				# for some reason, google stores blank passwords sometimes...
				if (password == "" or url == ""):
					continue
				passwords_holder["values"].append((
						url,
						username,
						password
					))
				if ("@" in username and username.lower() not in emails_gathered):
					# We'll use those emails on haveibeenpwned site
					emails_gathered.append(username.lower())
				count += 1
			except Exception as e:
				# Integrate a way to show errors if there is time
				passwords_holder["errors"].append(e)
		self.master.console.append(f"> Got {count} passwords from google.")

		self.master.chrome_pass_amount.setText(str(count))


# ScrapingFunctions(master = None).HaveIBeenPwned()