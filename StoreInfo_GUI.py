import csv
import sys
import os
import cv2
import datetime
import pandas as pd
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox
import face_recognition
from Encode import FaceEncoder

class App(QDialog):
    def __init__(self,cam_id):
        super().__init__()
        self.title = 'Smart Face Recognition System'
        x = int(cam_id) if cam_id=='0' else cam_id
        self.left = 50
        self.top = 50
        self.width = 640
        self.height = 480
        self.initUI()
        self.id_number = 0
        self.cap = cv2.VideoCapture(x)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)


        self.image_label = QLabel(self)
        self.image_label.resize(640, 480)


        self.capture_button = QPushButton('Capture', self)
        self.capture_button.resize(100, 50)
        self.capture_button.move(270, 430)
        self.capture_button.clicked.connect(self.capture_image)


        self.name_label = QLabel('Name:', self)
        self.name_textbox = QLineEdit(self)


        self.save_button = QPushButton('Save', self)
        self.save_button.resize(100, 50)
        self.save_button.move(270, 380)
        self.save_button.clicked.connect(self.save_info)


        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()

        hbox1.addWidget(self.name_label)
        hbox1.addWidget(self.name_textbox)

        vbox.addWidget(self.image_label)
        vbox.addWidget(self.capture_button)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addWidget(self.save_button)

        self.setLayout(vbox)
        self.show()

    def update_frame(self):
        ret, image = self.cap.read()
        if ret:
            # Reduce the resolution of the captured image
            image = cv2.resize(image, (320, 240), interpolation=cv2.INTER_AREA)

            # Detect the face and draw a bounding box
            face_locations = face_recognition.face_locations(image)
            if len(face_locations) > 0:
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, ch = image.shape
            bytes_per_line = ch * w
            q_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(q_image))


    def capture_image(self):
        self.timer.stop()
        last_id = -1
        for filename in os.listdir("./Images"):
            if filename.endswith(".png"):
                id_number = int(filename.split(".")[0])
                if id_number > last_id:
                    last_id = id_number

        self.id_number = last_id + 1

        ret, frame = self.cap.read()
        if not ret:
            QMessageBox.critical(self, "Error", "Failed to capture image!")
            return

        # Use the face_recognition library to detect faces in the image
        face_locations = face_recognition.face_locations(frame)

        if len(face_locations) == 0:
            QMessageBox.critical(self, "Error", "No face detected!")
            return
        elif len(face_locations) > 1:
            QMessageBox.critical(self, "Error", "Multiple faces detected!")
            return

        # Crop the image to include the face, hair, and ears
        top, right, bottom, left = face_locations[0]
        cropped = frame[top:bottom, left:right]

        # Resize the image to 216x216 pixels
        resized = cv2.resize(cropped, (216, 216), interpolation=cv2.INTER_AREA)


        # Save the image with the name as the ID number
        filename = f"./Images/{self.id_number}.png"
        cv2.imwrite(filename, resized)


        q_image = QImage(resized.data, 216, 216, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_image))

        # Restart the timer to resume the live view
        self.timer.start(1)

        QMessageBox.information(self, "Image Captured", f"Image Captured and Saved")
    def save_info(self):
        name = self.name_textbox.text()
        if name == '':
            QMessageBox.critical(self, "Error", "Please fill in all the fields!")
            return

        with open('./Model/Data/attendance.csv', 'a',newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self.id_number, name])

        self.name_textbox.clear()

        # Reset the ID number to zero
        self.id_number = 0

        self.timer.start(1)

        QMessageBox.information(self, "Success", "Information saved! Please Wait a while for encoding face data")
        folder_path = 'Images'
        file_path = 'EncodeFile.p'        
        face_encoder = FaceEncoder(folder_path)
        face_encoder.save_encodings(file_path)
        QMessageBox.information(self, "Success", "Done!!")
        try:
            self.cap.release()
            cv2.destroyAllWindows()
        except:
            pass
        self.close()


    def closeEvent(self, event):
        self.cap.release()
        cv2.destroyAllWindows()


