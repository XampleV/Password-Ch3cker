from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import *
import sys
from login_page.login_page import Ui_Form as login
from login_page.program_functions import login_functions

import tkinter as tk
import tkinter.messagebox

root = tk.Tk()
root.withdraw()
app = QApplication()

login_f = login_functions()
continue_app = {"start":False}

class MainWindow(QMainWindow):
	def __init__(self):
		
		QMainWindow.__init__(self)
		self.ui = login()
		self.ui.setupUi(self)
		self.CustomSettings()
		self.SetupButtons()
		self.show()
	def CustomSettings(self):
		self.setWindowTitle("Password Ch3cker - Login")
		self.ui.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
		self.ui.signup_password_input.setEchoMode(QtWidgets.QLineEdit.Password)
	def SetupButtons(self):
		self.ui.signup_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.signup_page))
		self.ui.already_a_user_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.login_page))
		self.ui.register_button.clicked.connect(lambda: self.register_func())
		self.ui.login_button.clicked.connect(lambda: self.login_func())
		self.ui.submit_auth_button.clicked.connect(lambda: self.check_code())

	def register_func(self):
		email, password = self.ui.signup_email_input.text(), self.ui.signup_password_input.text()
		if ("@" not in email):
			tkinter.messagebox.showerror("Invalid Email", "Please enter a valid email.")
			return
		if (password == ""):
			tkinter.messagebox.showerror("Invalid Password", "Please enter a valid password.")
			return
		
		# actually signing up here now...
		register = login_f.register_account(email, password)
		if (type(register) == str):
			tkinter.messagebox.showerror("Failure", f"Failed to create your account.\nError: {register}")
			return
		if (register == True):
			tkinter.messagebox.showinfo("Success", "Successfully created your account!")
			self.ui.stackedWidget.setCurrentWidget(self.ui.login_page)
			return
		tkinter.messagebox.showerror("Failed", "Failed to create your account!")
	def login_func(self):
		login = login_f.login_account(self.ui.email_input.text(), self.ui.password_input.text())
		if (login == True):
			self.ui.stackedWidget.setCurrentWidget(self.ui.auth_page)
			return
		tkinter.messagebox("Failure", "The credentials are incorrect.")
	def check_code(self):
		global continue_app
		check = login_f.check_code(self.ui.email_input.text(), self.ui.auth_code_input.text())
		if (check == True):
			continue_app["start"] = True
			tkinter.messagebox.showinfo('Success', "Successfully logged in!")
			root.destroy()
			return
		tkinter.messagebox.showerror("Failure", "Wrong code entered. ")




