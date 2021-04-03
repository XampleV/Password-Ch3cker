"""
Main point of this program is provide functionality to the UI buttons
There are functions here such as the sign up button, login, 2FA functions, etc. 

"""
import requests
import json
import os




server_url = (os.environ["YSU_HACKATHON_SERVER"])
api_key = (os.environ["YSU_HACKATHON_API"])

class login_functions:
	def register_account(self, email, password):
		register_request = requests.post(
			url = server_url,
			headers = {"X-API-KEY":api_key},
			json = {"email":email, "password":password, "action":"create"})
		if (register_request.text == "true"):
			return True
		return False
		
	def login_account(self, email, password):
		login_request = requests.post(
			url = server_url,
			headers = {"X-API-KEY":api_key},
			json = {"email":email, "password":password, "action":"login"})
		if(login_request.text == "true"):
			return True
	def check_code(self, email, code):
		check_request = requests.post(
			url = server_url, 
			headers = {"X-API-KEY":api_key},
			json = {"email":email, "code":int(code), "action":"check"})
		if (check_request.text == "true"):
			return True
		return False




