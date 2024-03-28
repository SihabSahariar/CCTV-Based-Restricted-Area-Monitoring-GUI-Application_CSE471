# Developed By Sihab Sahariar
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic import loadUi
from threading import Thread
import os
import live_view
from device_manager import *
class Home(QWidget):
    def __init__(self):
        super(Home,self).__init__()
        loadUi("Forms/home.ui",self)
        self.setWindowIcon(QIcon(":/icon/icon/dome_camera_80px.png")) 
        self.btn_live_view.clicked.connect(self.showLiveView)
        self.btn_device_manager.clicked.connect(self.deviceManagerFunction)
        self.setWindowTitle("CCTV Based Restricted Area Monitoring System ")
        #self.showMaximized()
    def showLiveView(self):
        self.close() 
        self.live = live_view.Live_view()

    def deviceManagerFunction(self):
        self.device = Device_Manager()
        self.device.show()
        self.device.showMaximized()
        self.close()
        
