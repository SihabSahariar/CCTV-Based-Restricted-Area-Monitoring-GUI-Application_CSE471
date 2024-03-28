import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QPushButton
)
from model.db import CameraDB
from view.registration_form import RegistrationForm

class MainWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        self.resize(300, 200)
        layout = QVBoxLayout()
        regButton = QPushButton('Register New Camera', self)
        regButton.clicked.connect(self.openRegistrationForm)
        layout.addWidget(regButton)
        self.setLayout(layout)
        self.setWindowTitle('Camera Registration Application')

    def openRegistrationForm(self):
        form = RegistrationForm(self.db, self)
        form.exec()


def main():
    app = QApplication(sys.argv)
    db = CameraDB()
    mainWindow = MainWindow(db)
    mainWindow.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
