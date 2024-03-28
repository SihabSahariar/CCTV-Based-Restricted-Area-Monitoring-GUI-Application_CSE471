# Developed By Sihab Sahariar
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from threading import Thread
from cores.draw import drawWidget
from camera_links import cameraConnect
# import qdarktheme
import os
from db import DataBase

db = DataBase()
import configparser
config = configparser.ConfigParser()
config.read('config.ini')


class ManualCamera(QWidget):
    def __init__(self):
        super(ManualCamera, self).__init__()
        loadUi("Forms/camera_manual.ui", self)
        self.setWindowTitle("Manual Add")
        self.setWindowIcon(QIcon(":/icon/icon/dome_camera_80px.png"))
        self.btn_add.clicked.connect(self.add_db)
        self.btn_cancel.clicked.connect(lambda: self.close())
        self.caml_links = cameraConnect().LoadCam()
        self.show()
        #################### Translation START ####################
        self.translate = config.getboolean('I/O', 'translate')
        
        # Translate
        if self.translate:
            self.retranslateUi()
        
        #################### Translation END ####################

    def retranslateUi(self):
        pass 
    
    def add_db(self):
        DeviceName = self.deviceName.text()
        IP = self.add_ip.text()
        UserName = self.add_username.text()
        Password = self.add_password.text()

        if DeviceName != "" and IP != "" and UserName != "" and Password != "":
            # db.insert(DeviceName, IP, UserName, Password)
            self.close()
            self.draw(DeviceName,IP,UserName,Password)
        else:
            self.msg = QMessageBox()
            self.msg.setIcon(QtWidgets.QMessageBox.Critical)
            self.msg.setInformativeText("Invalid Information!")
            self.msg.setWindowTitle("Error")
            self.msg.exec_()
            return
        
    def draw(self,DeviceName,IP,UserName,Password):
        id_cam = len(self.caml_links)
        x = drawWidget(id_cam,DeviceName,IP,UserName,Password) #index,cam_link
        dialog = QDialog()
        dialog.setWindowTitle("Draw Slots")
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(x)
        dialog.exec_()
