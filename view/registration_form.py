from PyQt6 import QtWidgets

class RegistrationForm(QtWidgets.QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()

        self.nameField = QtWidgets.QLineEdit(self)
        layout.addWidget(QtWidgets.QLabel("Camera Name:"))
        layout.addWidget(self.nameField)

        self.locationField = QtWidgets.QLineEdit(self)
        layout.addWidget(QtWidgets.QLabel("Camera Location:"))
        layout.addWidget(self.locationField)

        saveBtn = QtWidgets.QPushButton('Save', self)
        saveBtn.clicked.connect(self.saveCamera)
        layout.addWidget(saveBtn)

        self.setLayout(layout)
        self.setWindowTitle('Register New Camera')

    def saveCamera(self):
        name = self.nameField.text()
        location = self.locationField.text()
        self.db.add_camera(name, location)
        print(f"Saving Camera: {name}, Location: {location}")
        self.accept()
