from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
from threading import Lock
import numpy as np
import time
import cv2
import os
import threading
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'
os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
from Controller.newwindow import *
from  Controller.thread import *
from Controller.status import *
from camera_links import cameraConnect 
from graphics import resource
import home_
import psutil
from Model.db import Model as DataBase
import multiprocessing
import subprocess
from datetime import datetime
import signal

import pytest
from pytestqt import qtbot

db = DataBase("Model/databases/device_info.db")

def clickable(widget):
    class Filter(QObject):
        clicked = pyqtSignal()
        def eventFilter(self, obj, event):
            if obj == widget:
                if event.type() == QEvent.MouseButtonRelease:
                    self.clicked.emit()
                    return True
            return False

    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked

class Live_view(QWidget):
    def __init__(self):
        super(Live_view, self).__init__()
        loadUi("Views/live_view.ui",self)
        self.setWindowTitle("CCTV Based Restricted Area Monitoring System") 
        self.setWindowIcon(QIcon(":/icon/icon/dome_camera_80px.png"))
        self.show()
        self.showMaximized()    
        self.cam_links = cameraConnect().LoadCam()

        self.actual_cam = []+self.cam_links

        self.count = 0
        result = None

        for i in range(len(self.cam_links)):
            link = self.cam_links[i]
            try: 
                result = int(link)
                self.cam_links[i] = result
            except: 
                pass

        self.baki = 64-len(self.cam_links)
        i = 0
        while(i<self.baki):
        	self.cam_links.append("127.0.0.1")
        	i+=1      
        self.proc = [None for i in range(len(self.actual_cam))]
        self.actives = [False for i in range(len(self.cam_links))]
        self.labels = []
        self.threads = []
        self.records = []

        col = 4
        row = int(len(self.cam_links)/col) 
    
        # print(self.cam_links)
        for index, cam_link in enumerate(self.cam_links):
            flag = False
            try:
                if str(self.cam_links[index])==str(self.actual_cam[index]): 
                    th = ThreadVideo(self, cam_link, index)
                    th.imgSignal.connect(self.getImg)
                    self.threads.append(th)
                    th.start()
                    flag = True
            except Exception as e:
                # print("DEBUG_LIVE_VIEW: ",e)
                pass

            # Screen ---------------------
            self.lbl_cam = QLabel()
            self.lbl_cam.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            self.lbl_cam.setFont(QFont("Times", 12))
            self.lbl_cam.setStyleSheet("color: rgb(255,255,255);""background-color: rgb(30,30,30);""qproperty-alignment: AlignCenter;")

            clickable(self.lbl_cam).connect(partial(self.showCam, index))
            self.labels.append(self.lbl_cam)

            try:
                if index == 0 and flag:
                    self.layout.addWidget(self.lbl_cam, 0,0)
                elif index == 1 and flag:
                    self.layout.addWidget(self.lbl_cam, 0,1)
                elif index == 2 and flag:
                    self.layout.addWidget(self.lbl_cam, 1,0)
                elif index == 3 and flag:
                    self.layout.addWidget(self.lbl_cam, 1,1) 
            except:
                pass

        # Time Screen 
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showSystem)
        self.timer.start(1000)
        self.showSystem()

        # # Timer Auto Restart threads -
        # self.timer_th = QTimer(self)
        # self.timer_th.timeout.connect(self.refreshThread)
        # self.timer_th.start(60) # 60 secs

        self.newWindow = NewWindow(self)
        self.tableStatus = TableStatus(self)
        self.cam4()  
        self.btn_home.clicked.connect(self.ShowHome)
        self.process = []

    def refreshThread(self):        
        for i in self.threads:
            i.threadactive = True
            i.start()
    def killThread(self): 
        for i in self.threads:
            try:
                i.terminate()
                i.stop()
            except:
                pass
    def sizeHint(self):
        return QSize(width, height)

    def resizeEvent(self, event):
        self.update()

    @pyqtSlot(np.ndarray, int, bool,np.ndarray,bool,bool,str)
    def getImg(self, img, index, active,roi,detected,recognized,name):
        self.actives[index] = active
        if active:
            self.img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
            self.labels[index].setPixmap(QPixmap(self.img).scaled(self.labels[index].size(), Qt.KeepAspectRatio, Qt.FastTransformation) )
            if index == self.newWindow.index:
                self.newWindow.lbl_cam.setPixmap(QPixmap.fromImage(self.img))
        else:
            if index == self.newWindow.index:
                self.newWindow.close()

        face_detected = detected
        roi = QImage(roi.data.tobytes(), roi.shape[1], roi.shape[0], QImage.Format_RGB888)
        if face_detected:
            self.x = QLabel()
            self.x.setPixmap(QPixmap.fromImage(roi))
            self.verticalLayout_4.addWidget(self.x)
            vbar = self.scroll_detected.horizontalScrollBar() 
            vbar.setValue(vbar.maximum())

        face_recognized = recognized     
        if face_recognized:
            self.frameX = QFrame()
            self.verticalLayout = QVBoxLayout(self.frameX)
            self.xx = QLabel()
            self.xx.setPixmap(QPixmap.fromImage(roi))
            self.name = QLabel()
            self.name.setStyleSheet("color:white;")
            self.name.setText(name)
            self.verticalLayout.addWidget(self.xx)
            self.verticalLayout.addWidget(self.name)
            self.horizontalLayout.addWidget(self.frameX,alignment=Qt.AlignLeft)
            self.horizontalLayout.addStretch()
            hbar = self.scroll_recognized.verticalScrollBar() 
            hbar.setValue(hbar.maximum())  

    def showSystem(self):
        for index, (self.lbl_cam, active) in enumerate(zip(self.labels, self.actives)):
            if not active:
                self.lbl_cam.setPixmap(QPixmap(":/icon/icon/nocam.png"))

    def conv(self,img):
        w,h,ch = img.shape
        if img.ndim == 1:
            img =  cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

        qimg = QImage(img.data, h, w, 3*h, QImage.Format_RGB888) 
        qpixmap = QPixmap(qimg)

        return qpixmap

    def showCam(self, index):
        self.newWindow.index = index
        if not self.actives[index]:
            self.newWindow.lbl_cam.setPixmap(QPixmap(":/icon/icon/nocam.png"))
        self.newWindow.setWindowTitle('CAMERA {}'.format(index+1))
        self.newWindow.resize(1000,600)
        self.newWindow.show()
        # self.newWindow.showMaximized()

        
    def cam4(self):
        try:
            try:
                self.layout.itemAt(0).widget().setVisible(True)
            except:
                pass
            try:       
                self.layout.itemAt(1).widget().setVisible(True)
            except:
                pass
            try:       
                self.layout.itemAt(2).widget().setVisible(True)
            except:
                pass
            try:       
                self.layout.itemAt(3).widget().setVisible(True)
            except:
                pass

        except:
            QMessageBox.critical(self, "Camera Error", "You don't have sufficient camera")   

    def ShowHome(self): 
        for i in self.threads:
            try:
                i.stop()
            except:
                pass
        try:
            self.x = home_.Home()
            self.x.show()
        except:
            pass
        self.close()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = Live_view()
    app.exec_()
