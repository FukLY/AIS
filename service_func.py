from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
import requests
import json
import os


BASE_API_URL = 'http://127.0.0.1:5000/'


def get_table(table: QTableWidget, type_data: str = None):
    table.clear()
    list_column = ['Путь до файла', 'Размер файла в килобайтах']
    count_row = 0
    if type_data is None:
        r = requests.get(BASE_API_URL+'api/getallfilesinfo/')
        r = json.loads(r.text)
    else:
        r = requests.get(BASE_API_URL + 'api/filetype/?type={0}'.format(type_data))
        r = json.loads(r.text)
    table.setColumnCount(2)
    table.setHorizontalHeaderLabels(list_column)
    table.setRowCount(len(r['list_file']))
    while count_row < len(r['list_file']):
        item_path = QTableWidgetItem()
        item_path.setText(r['list_file'][count_row])
        table.setItem(count_row, 0, item_path)

        r_size = requests.get(BASE_API_URL+'api/filesize/?filename={0}'.format(r['list_file'][count_row]))
        r_size = json.loads(r_size.text)
        item_size_file = QTableWidgetItem()
        item_size_file.setText(r_size['size'] + ' Кб')
        table.setItem(count_row, 1, item_size_file)
        count_row += 1

    return table