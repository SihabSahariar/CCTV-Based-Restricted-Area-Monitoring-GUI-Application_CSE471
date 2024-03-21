# main.py
import sys
from PyQt6 import QtWidgets
from model.db import CameraDB
from view.registration_form import RegistrationForm

class MainWindow(QtWidgets.QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()
        regButton = QtWidgets.QPushButton('Register New Camera', self)
        regButton.clicked.connect(self.openRegistrationForm)
        layout.addWidget(regButton)
        self.setLayout(layout)
        self.setWindowTitle('Camera Registration Application')

    def openRegistrationForm(self):
        form = RegistrationForm(self.db, self)
        form.exec()

def main():
    app = QtWidgets.QApplication(sys.argv)
    db = CameraDB()
    mainWindow = MainWindow(db)
    mainWindow.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
