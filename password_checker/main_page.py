from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import *
import threading
from PyQt5.QtCore import QTimer, QEventLoop

from password_checker.main_page_ui import Ui_Form as pswd_checker
from password_checker.password_checker_functions import GetAllBrowsers, ScrapingFunctions, passwords_holder, results_holder

import tkinter as tk
import tkinter.messagebox

root = tk.Tk()
root.withdraw()
new_app = QApplication()

class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.ui = pswd_checker()
		self.ui.setupUi(self)
		self.CustomSettings()
		self.SetupButtons()
		self.show()
	def CustomSettings(self):
		self.setWindowTitle("Password Ch3cker - By Moe Alshoubaki")
	def SetupButtons(self):
		self.ui.accept_button.clicked.connect(lambda: self.fetch_passwords())
		self.ui.start_button.clicked.connect(lambda: self.start_main_function())
		self.ui.full_summary_button.clicked.connect(lambda:self.ui.stackedWidget.setCurrentWidget(self.ui.summary_page))

		# QTables Connection here
		self.ui.leaked_data_button.clicked.connect(self.change_to_leaked)
		self.ui.weak_passwords_button.clicked.connect(self.change_to_weak)
		self.ui.reacurring_passwords_button.clicked.connect(self.change_to_reaccuring)

		# Return button from summary menu
		self.ui.go_back_from_summary.clicked.connect(lambda:self.ui.stackedWidget.setCurrentWidget(self.ui.scrape_page))


	def change_to_leaked(self):
		self.ui.QTable_Summaries.setCurrentWidget(self.ui.leaked_data_page)
		self.ui.title_of_table.setText("Leaked Data")
	def change_to_weak(self):
		self.ui.QTable_Summaries.setCurrentWidget(self.ui.weak_passwords)
		self.ui.title_of_table.setText("Weak Passwords")
	def change_to_reaccuring(self):
		self.ui.QTable_Summaries.setCurrentWidget(self.ui.reaccuring_passwords_page)
		self.ui.title_of_table.setText("Re-accuring Passwords")



	def fetch_passwords(self):
		self.ui.console.append("> Fetching browser passwords...")
		self.ui.stackedWidget.setCurrentWidget(self.ui.fetching_page)
		threading.Thread(target = GetAllBrowsers, args=(self.ui,), daemon = False).start()


		loop = QEventLoop()
		QTimer.singleShot(3000, loop.quit)
		loop.exec_()
		self.ui.stackedWidget.setCurrentWidget(self.ui.scrape_page)
	def start_main_function(self):
		self.ui.start_button.setEnabled(False)
		ScrapingController = ScrapingFunctions(master = self.ui)
		threading.Thread(target = ScrapingController.FilterPasswords, daemon = False).start()
		threading.Thread(target = ScrapingController.HaveIBeenPwned, daemon = False).start()


