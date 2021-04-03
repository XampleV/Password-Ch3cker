# Created by Moe Alshoubaki
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import *
import tkinter as tk
import tkinter.messagebox

from login_page.login import MainWindow, app, continue_app

class LoginPage():
	def __init__(self):
		self.login = MainWindow()
		app.exec_()

class MainPage():
	def __init__(self):
		self.main = MainWindow()
		new_app.exec_()


if __name__ == "__main__":
	window = LoginPage()
	app.shutdown()

	if (continue_app["start"] == True):
		from password_checker.main_page import MainWindow, new_app

		
		window = MainPage()