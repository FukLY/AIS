import os.path

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, QAction, QGridLayout,QComboBox,QLabel,
                             QLineEdit, QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem, QProgressBar, QDateEdit,
                             QVBoxLayout, QHBoxLayout, QFormLayout,QGroupBox, QCheckBox,QCalendarWidget,
                             QFileDialog,QMenu,QListWidget, QMouseEventTransition)
from PyQt5.QtGui import QIcon, QColor, QCursor
from PyQt5.QtCore import pyqtSlot, QSize, Qt, QThread, pyqtSignal
from PyQt5.QtCore import QEventLoop, QUrl
import sys
import requests
import json
import view_form_file
from pyrogram import Client
import service
import random


class AuthForm(QWidget):

    def __init__(self):
        super().__init__()
        self.BASE_API_URL = 'http://127.0.0.1:5000/'
        self.label_login = QLabel()
        self.lineedit_login = QLineEdit()
        self.label_password = QLabel()
        self.lineedit_password = QLineEdit()
        self.button_auth = QPushButton()
        self.grid_layout = QGridLayout()
        self.id_user = 0
        self.temp_password = ''
        self.init_ui()

    def init_ui(self):
        self.grid_layout.setSpacing(8)
        self.button_auth.setText('Авторизоваться')
        self.button_auth.setIcon(QIcon('ico/login.ico'))
        self.setWindowTitle('Форма авторизации')
        self.setWindowIcon(QIcon('ico/login.ico'))
        self.label_login.setText('Введите Ваш логин:')
        self.label_password.setText('Введите Ваш пароль:')
        self.grid_layout.addWidget(self.label_login, 3, 0)
        self.grid_layout.addWidget(self.lineedit_login, 3, 1)
        self.button_get_password = QPushButton()
        self.button_get_password.setText('Получить пароль в Telegram')
        self.button_get_password.setIcon(QIcon('ico/telegram.ico'))
        self.grid_layout.addWidget(self.label_password, 4, 0)
        self.grid_layout.addWidget(self.lineedit_password, 4, 1)
        self.grid_layout.addWidget(self.button_get_password, 5, 1)
        self.tg_label = QLabel()
        self.tg_label.setText('Укажите Ваш пароль из сообщения в Telegram:')
        self.tg_lineedit = QLineEdit()
        self.tg_label.setVisible(False)
        self.tg_lineedit.setVisible(False)
        self.grid_layout.addWidget(self.tg_label, 6, 0)
        self.grid_layout.addWidget(self.tg_lineedit, 6, 1)

        self.grid_layout.addWidget(self.button_auth, 7, 1)
        self.setLayout(self.grid_layout)
        self.setGeometry(300, 300, 350, 300)
        self.button_auth.clicked.connect(self.button_auth_clicked)
        self.button_get_password.clicked.connect(self.button_tg_send)

        self.show()

    def button_tg_send(self):
        self.tg_label.setVisible(True)
        self.tg_lineedit.setVisible(True)
        r = requests.get(self.BASE_API_URL+'api/postcode/?username={0}'.format(self.lineedit_login.text()))
        code_app = json.loads(r.text)
        code_app = code_app['code']
        random_phone = service.LIST_PHONE[random.randint(0, len(service.LIST_PHONE) - 1)]
        print(random_phone)
        application = Client(os.path.join('session_tg', str(random_phone)), service.API_ID, service.API_HASH)
        application.start()
        application.send_message(chat_id=self.lineedit_login.text(),
                                 text='Your code for enter to application:\n{0}'.format(code_app))
        application.stop()

    def button_auth_clicked(self):
        r = requests.get(self.BASE_API_URL+'api/userauth/?login={0}&password={1}&code={2}'.format(self.lineedit_login.text(),
                                                                                         self.lineedit_password.text(),
                                                                                                  self.tg_lineedit.text()))
        json_text = json.loads(r.text)
        try:
            self.id_user = json_text['id_user']
            self.temp_password = json_text['temp_password']
            self.form_view_file = view_form_file.ViewFileForm(temp_password=self.temp_password, id_user=self.id_user)
            self.form_view_file.show()
        except Exception as e:
            print(e)
            QMessageBox.warning(self, "Ошибка", "Не правильный логин или пароль")





app = QApplication(sys.argv)
ex = AuthForm()
sys.exit(app.exec_())