import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget
import csv
import pytest
from pytestqt import qtbot
class FaceData(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('Face Records')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)

        self.load_data()

    def load_data(self):
        try:
            with open('Model/Data/attendance.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                data = list(reader)

                headers = data[0]
                self.table_widget.setColumnCount(len(headers))
                self.table_widget.setHorizontalHeaderLabels(headers)

                self.table_widget.setRowCount(len(data) - 1)

                for i, row in enumerate(data[1:]):
                    for j, col in enumerate(row):
                        self.table_widget.setItem(i, j, QTableWidgetItem(col))

        except FileNotFoundError:
            print("File not found!")


