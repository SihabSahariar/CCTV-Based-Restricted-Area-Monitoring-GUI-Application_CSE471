import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt
from datetime import datetime

import pytest
from pytestqt import qtbot

class AttendanceLogs(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Attendance Logs')
        self.setGeometry(100, 100, 800, 400)
        layout = QVBoxLayout(self)

        self.table = QTableWidget(self)
        layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        try:
            with open('Info_Saved.txt', 'r') as file:
                data = [line.strip() for line in file.readlines()]

            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Recognized Time'])
            self.table.setRowCount(len(data))

            for i, row in enumerate(data):
                col_data = row.split(', ')
                for j, col in enumerate(col_data):
                    item = QTableWidgetItem(col)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    if j == 2 and col.startswith('Recognized Time: '):  # Check for time column
                        time_str = col.split(': ')[1]  
                        time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
                        formatted_time = time_obj.strftime("%Y-%m-%d %H:%M:%S")
                        item.setText(formatted_time)
                    elif j == 0 or j == 1:
                        item.setText(col.split(': ')[1])
                    self.table.setItem(i, j, item)

        except FileNotFoundError:
            print("File not found.")


