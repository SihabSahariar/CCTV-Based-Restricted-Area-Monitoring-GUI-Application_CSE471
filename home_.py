import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic import loadUi
from threading import Thread
import os
import live_view
from device_manager import *
from camera_links import cameraConnect 
from StoreInfo_GUI import App
from attendanceLogs import *
from faceRecords import *

import pytest
from pytestqt import qtbot
class Home(QWidget):
    def __init__(self):
        super(Home,self).__init__()
        loadUi("Views/home.ui",self)
        self.setWindowIcon(QIcon(":/icon/icon/dome_camera_80px.png")) 
        self.btn_live_view.clicked.connect(self.showLiveView)
        self.btn_device_manager.clicked.connect(self.deviceManagerFunction)
        # self.btn_settings.clicked.connect(self.addFaceFunction)
        # self.btn_logs.clicked.connect(self.log)
        # self.btn_about.clicked.connect(self.about)
        # self.btnFace.clicked.connect(self.faceRecords)
        self.btn_settings.setVisible(False)
        self.btn_logs.setVisible(False)
        self.btnFace.setVisible(False)
        self.btn_about.setVisible(False)
        self.setWindowTitle("CCTV Based Restricted Area Monitoring System")
        self.cam_links = cameraConnect().LoadCam()
        self.passcam = self.cam_links[0] if self.cam_links else -1
        self.showMaximized()
    def showLiveView(self):
        self.close() 
        self.live = live_view.Live_view()

    def deviceManagerFunction(self):
        self.device = Device_Manager()
        self.device.show()
        self.device.showMaximized()
        self.close()

    def addFaceFunction(self):
        self.add = App(self.passcam)
        self.add.show()     
    def log(self):
        self.attendance_logs = AttendanceLogs()
        self.attendance_logs.show()

    def faceRecords(self):
        self.face_records = FaceData()
        self.face_records.show()
        
    def about(self):
        QMessageBox.information(self, "About Software", "Developed By Group 04")