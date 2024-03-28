import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFileDialog, QMessageBox
from shutil import copyfile, copytree, rmtree

class DatabaseTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Tool")
        self.setGeometry(100, 100, 400, 200)

        # Apply Dark Theme
        self.setStyleSheet("background-color: #333; color: white;")
        

        self.restore_button = QPushButton("Restore Database", self)
        self.restore_button.setGeometry(50, 50, 150, 30)
        self.restore_button.clicked.connect(self.restore_database)

        self.backup_button = QPushButton("Backup Database", self)
        self.backup_button.setGeometry(200, 50, 150, 30)
        self.backup_button.clicked.connect(self.backup_database)

        self.status_label = QLabel(self)
        self.status_label.setGeometry(50, 100, 300, 30)

    def restore_database(self):
        database_file, _ = QFileDialog.getOpenFileName(self, "Select Database File", "", "Database Files (*.db)")
        if database_file:
            detected_person_dir = QFileDialog.getExistingDirectory(self, "Select 'detected_person' Directory")
            if detected_person_dir:
                try:
                    copyfile(database_file, "database.db")
                    copytree(detected_person_dir, "detected_person")
                    self.status_label.setText("Database restored successfully.")
                except Exception as e:
                    self.status_label.setText(f"Error: {str(e)}")
            else:
                self.status_label.setText("No 'detected_person' directory selected.")
        else:
            self.status_label.setText("No database file selected.")

    def backup_database(self):
        backup_path = QFileDialog.getExistingDirectory(self, "Select Backup Path")
        if backup_path:
            try:
                copyfile("database.db", os.path.join(backup_path, "database.db"))
                copytree("detected_person", os.path.join(backup_path, "detected_person"))
                self.status_label.setText("Database backed up successfully.")
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)}")
        else:
            self.status_label.setText("No backup path selected.")

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = DatabaseTool()
#     window.show()
#     sys.exit(app.exec_())
