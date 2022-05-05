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
import service_func
import os


class ViewFileForm(QWidget):

    def __init__(self, temp_password: str, id_user: str):
        super().__init__()
        self.seen = 0
        self.temp_password = temp_password
        self.id_user = id_user
        self.BASE_API_URL = 'http://127.0.0.1:5000/'
        self.table = QTableWidget()
        self.combobox = QComboBox()
        self.label = QLabel()
        self.button_push = QPushButton()
        self.grid = QGridLayout()
        self.init_ui()

    def init_ui(self):
        self.button_push.setText('Обновить таблицу')
        self.button_push.setIcon(QIcon('ico/update.ico'))
        self.setWindowIcon(QIcon('ico/view.ico'))
        self.setWindowTitle('Просмотр')
        self.label.setText('Выбрать тип файла:')
        self.combobox.addItem('TXT')
        self.combobox.addItem('JPG')
        self.grid.addWidget(self.label, 1, 1)
        self.grid.addWidget(self.combobox, 2, 1)
        self.grid.addWidget(self.button_push, 3, 1)
        self.button_push.clicked.connect(self.button_clicked)
        self.grid.addWidget(service_func.get_table(self.table), 4, 1)
        self.table.viewport().installEventFilter(self)
        self.setLayout(self.grid)
        self.table.resizeColumnsToContents()
        self.setGeometry(300, 300, 350, 300)

    def button_clicked(self):
        service_func.get_table(table=self.table, type_data=self.combobox.currentText())
        self.seen += 1

    # RIGHT CLIK ON TABLE ITEM. filter by button mouse.
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseButtonDblClick and
                event.buttons() == QtCore.Qt.LeftButton and
                source is self.table.viewport()):

            #проверка временной метки
            #если метка устаревшая, то выкидываем из формы. Открываем форму авторизации.
            #шифрование переселымаех данных

            item = self.table.itemAt(event.pos())
            if item is not None:
                r = requests.get(self.BASE_API_URL + 'api/isliveuser/?'
                                                     'temp_password={0}&id_user={1}'.format(self.temp_password,
                                                                                            self.id_user))
                r = json.loads(r.text)
                if r['status'] == 0:
                    row = self.table.itemAt(event.pos()).row()
                    self.filedialog = QFileDialog()
                    self.filedialog.setWindowIcon(QIcon('ico/view.ico'))
                    self.filedialog.setFileMode(QFileDialog.DirectoryOnly)
                    self.folder = self.filedialog.getExistingDirectory()
                    filename = str(self.table.item(row, 0).text())
                    need_filename = filename.split('\\')[len(filename.split('\\')) - 1]
                    if not os.path.exists('files_download'):
                        os.mkdir('files_download')
                    r = requests.get(self.BASE_API_URL + 'api/getfile/?filename={0}'.format(filename))
                    path_save = os.path.join(self.folder, 'files_download')
                    f = open(os.path.join(path_save, need_filename), 'wb')
                    f.write(r.content)
                    f.close()
                else:
                    QMessageBox.warning(self, "Ошибка", "Необходима повторная авторизация")
        return super(ViewFileForm, self).eventFilter(source, event)

