# Developed By Sihab Sahariar
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from threading import Thread
import graphics.resource
import os
from db import DataBase
from PyQt5 import QtCore, QtGui, QtWidgets
from camera_manual import *
import home_
from camera_links import cameraConnect
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
class Device_Manager(QWidget):
    def __init__(self):
        super(Device_Manager, self).__init__()
        loadUi("Forms/device_manager.ui", self)
        # self.db = DataBase("modules/databases/device_info.db")
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("database.db")
        self.model = QSqlTableModel()
        self.delrow = -1
        self.setWindowTitle("Device Manager")
        self.setWindowIcon(QIcon(":/icon/icon/dome_camera_80px.png"))
        #################### Translation START ####################
        self.translate = config.getboolean('I/O', 'translate')
        
        # Translate
        if self.translate:
            self.retranslateUi()
        
        #################### Translation END ####################
        #         
        #Link to the buttons
        self.btn_home.clicked.connect(self.ShowHome)
        self.btn_manual.clicked.connect(self.add_db)
        self.btn_refresh.clicked.connect(self.populate)
        self.btn_delete.clicked.connect(self.delete)

        #Hide unnecessary widgets
        self.OnlineDeviceList.setVisible(False)
        self.btn_delete.setVisible(False)
        self.btn_manual.setVisible(False)
        self.btn_refresh.setVisible(False)
        self.btn_about.setVisible(False)
        #self.AddedCamera.setVisible(False)
        self.btn_home.setVisible(False)

        #Show in Center Screen
        qtRectangle = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.populate()



    def retranslateUi(self):
        self.setWindowTitle("GK AI VMS - 장치 관리자")
        self.label_3.setText("")
        self.label.setText("AI 스마트 주차 시스템")
        self.btn_home.setText("집")
        self.btn_about.setText("정보")
        self.label_4.setText("Copyright©2023, GK AI. 모든 권리 보유.")
        self.label_2.setText("온라인 장치:")
        self.btn_manual.setText("수동 추가")
        self.btn_refresh.setText("새로 고침")
        self.btn_delete.setText("삭제")
        self.label_5.setText("")

    def ShowHome(self):
        self.ui = home_.Home()
        self.ui.show()
        self.close()

    def add_db(self):
        self.x = ManualCamera()
        self.populate()

    def populate(self):
        self.initializeModel(self.model)
        self.online_total.setText(str(self.model.rowCount()))
        self.AddedCamera.setModel(self.model)
        self.AddedCamera.setColumnHidden(3, True)  # Hide the "Username" column
        self.AddedCamera.setColumnHidden(4, True)  # Hide the "Password" column
        # self.AddedCamera.setColumnHidden(5, True)  # Hide the "Sample Image Path" column
        self.AddedCamera.setColumnHidden(6, True)  # Hide the "Last Updated" column
        self.AddedCamera.setColumnHidden(7, True)  # Hide the "Last Updated" column
        self.AddedCamera.setColumnHidden(8, True) # Hide the "Last Updated" column
        self.AddedCamera.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.AddedCamera.clicked.connect(self.findrow)
        self.OnlineDeviceList.setModel(self.model)
        self.OnlineDeviceList.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cam_links = cameraConnect().LoadCam()

    def delete(self):
        self.model.removeRow(self.AddedCamera.currentIndex().row())
        self.populate()

    def initializeModel(self, model):       
        if self.translate:
            self.HEADER = ["ID", "카메라 이름", "IP 주소","","","위치","샘플 이미지 경로"]
        else:
            self.HEADER = ["ID", "Camera Name", "IP Address","","","Location","Sample Image Path"]

        self.model.setTable("camera")
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.model.select()
        for i in range(len(self.HEADER)):
            self.model.setHeaderData(i, Qt.Horizontal, self.HEADER[i])

    def addrow(self):
        ret = self.model.insertRows(self.model.rowCount(), 1)

    def findrow(self, i):
        self.delrow = i.row()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Device_Manager()
    window.show()
    app.exec_()
