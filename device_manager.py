import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from threading import Thread
from graphics import resource
import os
from Model.db import Model as DataBase
from PyQt5 import QtCore, QtGui, QtWidgets
from camera_manual import *
import home_

import pytest
from pytestqt import qtbot
class Device_Manager(QWidget):
    def __init__(self):
        super(Device_Manager, self).__init__()
        loadUi("Views/device_manager.ui",self)
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('Model/databases/device_info.db')     
        self.model = QSqlTableModel()
        self.delrow = -1       
        self.setWindowTitle("Device Manager") 
        self.setWindowIcon(QIcon(":/icon/icon/dome_camera_80px.png")) 
        self.btn_home.clicked.connect(self.ShowHome)
        self.btn_manual.clicked.connect(self.add_db)
        self.btn_refresh.clicked.connect(self.populate)
        self.btn_delete.clicked.connect(self.delete) 
        self.populate()

    def ShowHome(self):
        self.ui = home_.Home()
        self.ui.show()
        self.ui.showMaximized()
        self.close()

    def add_db(self):
        self.x = ManualCamera()
        self.x.show()
        self.populate()
    def populate(self):
        self.initializeModel(self.model)
        self.online_total.setText(str(self.model.rowCount()))
        self.AddedCamera.setModel(self.model)
        self.AddedCamera.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.AddedCamera.clicked.connect(self.findrow)
        self.OnlineDeviceList.setModel(self.model)
        self.OnlineDeviceList.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
             
    def delete(self):
    	self.model.removeRow(self.AddedCamera.currentIndex().row())
    	self.populate()

    def initializeModel(self,model):
    	self.HEADER = ["ID", "Device Name", "Additional Information", "Camera Group","Login Type", "IP", "Port","User Name","Password","Protocol"]         
    	self.model.setTable('data')
    	self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
    	self.model.select()
    	for i in range(len(self.HEADER)):
    	    self.model.setHeaderData(i,Qt.Horizontal,self.HEADER[i])

    def addrow(self):
    	ret = self.model.insertRows(self.model.rowCount(), 1)

    def findrow(self,i):
    	self.delrow = i.row()

                  
# if __name__ == "__main__":
#      app = QApplication(sys.argv)
#      window = Device_Manager()
#      window.show()
#      app.exec_()

