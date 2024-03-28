# Developed By Sihab Sahariar
from PyQt5 import QtWidgets
from functools import partial
from threading import Lock
import numpy as np
# import time
# import cv2
import os
# import threading
from threading import Thread
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'
os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(QLibraryInfo.PluginsPath)
from cores.windownew import *
import cores.thread #import Thread
from cores.status import *
from camera_links import cameraConnect 
from cores.draw import drawWidget
from cores.redraw import RedrawSlot
from device_manager import *
from Forms import resource
# import home_
# import psutil
# from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import shutil
from about import About
from config import ConfigApp
from db import DataBase
from sqlalchemy.orm import sessionmaker
from database_setup import *
from detector.YOLOv8 import YOLOv8
# os.environ['CUDA_VISIBLE_DEVICES']='cuda'
import configparser
from map_widget import *
from generate_report import *
from db_tool import *
config = configparser.ConfigParser()
config.read('config.ini')
full_frame_path = config['DEFAULT']['full_frame_dir']

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
        loadUi("Forms/live_view.ui",self)
        self.setWindowTitle("CCTV Based Restricted Area Monitoring System - Live View") 
        self.setWindowIcon(QIcon(":/icon/icon/dome_camera_80px.png"))
        self.show()
        self.showMaximized()   
        # Hide Unnecessary Widgets
        self.widget_2.setVisible(False)
        #self.widget_devicemgr.setVisible(False)
        self.btn_home.setVisible(False)
        
        # Add Map
        self.map_widget = MapDisplay()
        self.horizontalLayout_99.addWidget(self.map_widget)
        #################### Translation START ####################
        self.translate = config.getboolean('I/O', 'translate')
        
        # Translate
        if self.translate:
            self.retranslateUi()
        
        #################### Translation END ####################

        self.cam_links = cameraConnect().LoadCam()
        self.cam_links_draw = cameraConnect().LoadCam()
        self.actual_cam = []+self.cam_links
        self.count = 0
        result = None
        self.btn_addr = []
        self.modified = []
        self.camera_check = []

        self.baki = 64-len(self.cam_links)
        i = 0
        while(i<self.baki):
            self.cam_links.append("127.0.0.1") 
            i+=1      
        self.proc = [None for i in range(len(self.actual_cam))]
        self.actives = [False for i in range(len(self.cam_links))]
        self.labels = []
        self.threads = []
        self.newAdded = False
        # Camera Grid 
        col = 4
        row = int(len(self.cam_links)/col) 
        for index, cam_link in enumerate(self.cam_links):
            try:
                if str(self.cam_links[index])==str(self.actual_cam[index]): 
                    th = cores.thread.ThreadVideo(self, cam_link, index)#,self.model)
                    th.imgSignal.connect(self.getImg)
                    self.threads.append(th)

                    # Map ---------------------
                    check_box = QCheckBox(f"Camera {index+1}")
                    self.verticalLayout_5.addWidget(check_box)
                    # check_box.stateChanged.connect(partial(self.map_widget.changeDashboardWindowCheckboxStatus, check_box.isChecked()))
                    self.camera_check.append(check_box)
                    # ---------------------

            except:
                    pass
            # Screen ---------------------
            self.lbl_cam = QLabel()
            self.lbl_cam.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            # self.lbl_cam.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.lbl_cam.setFont(QFont("Times", 12))
            self.lbl_cam.setStyleSheet("color: rgb(255,255,255);""background-color: rgb(80,80,80);""qproperty-alignment: AlignCenter;")
            clickable(self.lbl_cam).connect(partial(self.showCam, index)) 
            self.comboBox = QComboBox()  
            self.labels.append(self.lbl_cam)



            try:
                if index == 0:
                    self.layout.addWidget(self.lbl_cam, 1, 0)
                elif index == 1:
                    self.layout.addWidget(self.lbl_cam, 1, 1)
                elif index == 2:
                    self.layout.addWidget(self.lbl_cam, 3, 0)
                elif index == 3:
                    self.layout.addWidget(self.lbl_cam, 3, 1)
                elif index == 4:
                    self.layout.addWidget(self.lbl_cam, 1, 2)
                elif index == 5:
                    self.layout.addWidget(self.lbl_cam, 1, 3)
                elif index == 6:
                    self.layout.addWidget(self.lbl_cam, 3, 2)
                elif index == 7:
                    self.layout.addWidget(self.lbl_cam, 3, 3)
                elif index == 8:
                    self.layout.addWidget(self.lbl_cam, 5, 0)
                elif index == 9:
                    self.layout.addWidget(self.lbl_cam, 5, 1)
                elif index == 10:
                    self.layout.addWidget(self.lbl_cam, 5, 2)
                elif index == 11:
                    self.layout.addWidget(self.lbl_cam, 5, 3)
                elif index == 12:
                    self.layout.addWidget(self.lbl_cam, 7, 0)
                elif index == 13:
                    self.layout.addWidget(self.lbl_cam, 7, 1)
                elif index == 14:
                    self.layout.addWidget(self.lbl_cam, 7, 2)
                elif index == 15:
                    self.layout.addWidget(self.lbl_cam, 7, 3)
                elif index == 16:
                    self.layout.addWidget(self.lbl_cam, 1, 4)
                elif index == 17:
                    self.layout.addWidget(self.lbl_cam, 1, 5)
                elif index == 18:
                    self.layout.addWidget(self.lbl_cam, 1, 6)
                elif index == 19:
                    self.layout.addWidget(self.lbl_cam, 1, 7)
                elif index == 20:
                    self.layout.addWidget(self.lbl_cam, 3, 4)
                elif index == 21:
                    self.layout.addWidget(self.lbl_cam, 3, 5)
                elif index == 22:
                    self.layout.addWidget(self.lbl_cam, 3, 6)
                elif index == 23:
                    self.layout.addWidget(self.lbl_cam, 3, 7)
                elif index == 24:
                    self.layout.addWidget(self.lbl_cam, 5, 4)
                elif index == 25:
                    self.layout.addWidget(self.lbl_cam, 5, 5)
                elif index == 26:
                    self.layout.addWidget(self.lbl_cam, 5, 6)
                elif index == 27:
                    self.layout.addWidget(self.lbl_cam, 5, 7)
                elif index == 28:
                    self.layout.addWidget(self.lbl_cam, 7, 4)
                elif index == 29:
                    self.layout.addWidget(self.lbl_cam, 7, 5)
                elif index == 30:
                    self.layout.addWidget(self.lbl_cam, 7, 6)
                elif index == 31:
                    self.layout.addWidget(self.lbl_cam, 7, 7)
                elif index == 32:
                    self.layout.addWidget(self.lbl_cam, 9, 0)
                elif index == 33:
                    self.layout.addWidget(self.lbl_cam, 9, 1)
                elif index == 34:
                    self.layout.addWidget(self.lbl_cam, 9, 2)
                elif index == 35:
                    self.layout.addWidget(self.lbl_cam, 9, 3)
                elif index == 36:
                    self.layout.addWidget(self.lbl_cam, 9, 4)
                elif index == 37:
                    self.layout.addWidget(self.lbl_cam, 9, 5)
                elif index == 38:
                    self.layout.addWidget(self.lbl_cam, 9, 6)
                elif index == 39:
                    self.layout.addWidget(self.lbl_cam, 9, 7)
                elif index == 40:
                    self.layout.addWidget(self.lbl_cam, 11, 0)
                elif index == 41:
                    self.layout.addWidget(self.lbl_cam, 11, 1)
                elif index == 42:
                    self.layout.addWidget(self.lbl_cam, 11, 2)
                elif index == 43:
                    self.layout.addWidget(self.lbl_cam, 11, 3)
                elif index == 44:
                    self.layout.addWidget(self.lbl_cam, 11, 4)
                elif index == 45:
                    self.layout.addWidget(self.lbl_cam, 11, 5)
                elif index == 46:
                    self.layout.addWidget(self.lbl_cam, 11, 6)
                elif index == 47:
                    self.layout.addWidget(self.lbl_cam, 11, 7)
                elif index == 48:
                    self.layout.addWidget(self.lbl_cam, 13, 0)
                elif index == 49:
                    self.layout.addWidget(self.lbl_cam, 13, 1)
                elif index == 50:
                    self.layout.addWidget(self.lbl_cam, 13, 2)
                elif index == 51:
                    self.layout.addWidget(self.lbl_cam, 13, 3)
                elif index == 52:
                    self.layout.addWidget(self.lbl_cam, 13, 4)
                elif index == 53:
                    self.layout.addWidget(self.lbl_cam, 13, 5)
                elif index == 54:
                    self.layout.addWidget(self.lbl_cam, 13, 6)
                elif index == 55:
                    self.layout.addWidget(self.lbl_cam, 13, 7)
                elif index == 56:
                    self.layout.addWidget(self.lbl_cam, 15, 0)
                elif index == 57:
                    self.layout.addWidget(self.lbl_cam, 15, 1)
                elif index == 58:
                    self.layout.addWidget(self.lbl_cam, 15, 2)
                elif index == 59:
                    self.layout.addWidget(self.lbl_cam, 15, 3)
                elif index == 60:
                    self.layout.addWidget(self.lbl_cam, 15, 4)
                elif index == 61:
                    self.layout.addWidget(self.lbl_cam, 15, 5)
                elif index == 62:
                    self.layout.addWidget(self.lbl_cam, 15, 6)
                elif index == 63:
                    self.layout.addWidget(self.lbl_cam, 15, 7)
            except:
                pass


        self.update_slots()

        # Time Screen ----------------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showSystem)
        self.timer.start(1000)
        self.showSystem()
        # ----------------------------
        self.newWindow = NewWindow(self)
        self.tableStatus = TableStatus(self)

        if len(self.threads)>32:
            self.cam64()
        elif len(self.threads)>16:
            self.cam32()
        elif len(self.threads)>8:
            self.cam16()
        elif len(self.threads)>4:
            self.cam8()
        elif len(self.threads)>1:
            self.cam4()
        else:
            self.cam1()

        self.btn_camera_add.clicked.connect(self.showaddCamera)      
        self.btn_add.clicked.connect(self.add_db)
        self.btn_cleardb.clicked.connect(self.clear_db)
        self.btn_devicemgr.clicked.connect(self.showDeviceMgr)
        self.btn_about.clicked.connect(self.showAbout)
        self.btn_lukao.clicked.connect(self.showLukao)
        self.btn_config.clicked.connect(self.showConfig)
        self.btn_map.clicked.connect(self.showMap)
        self.btn_print.clicked.connect(self.printShow)
        self.btn_db_tool.clicked.connect(self.dbTool)


        self.terrian_view_btn.clicked.connect(self.map_widget.setTerrainView)
        self.setellite_view_btn.clicked.connect(self.map_widget.setSatelliteView)
        # self.map_widget.changeDashboardWindowCheckboxStatus.connect(self.update_checkbox_status_for_map)


        self.process = []
        self.new_count = 0
        
        self.show()

    def update_checkbox_status_for_map(self, status):
        self.terrian_view_btn.setChecked(status)
        self.setellite_view_btn.setChecked(not status)
        # self.map_widget.setTerrainView() if status else self.map_widget.setSatelliteView()

    def dbTool(self):
        self.db_tool = DatabaseTool()
        self.db_tool.show()

    def printShow(self):
        self.report = PDFGenerator()
        self.report.show()

    def showMap(self):
        if self.btn_map.text() == "Map":
            self.stackedWidget.setCurrentIndex(1)
            self.btn_map.setText("Live View")
        elif self.btn_map.text() == "Live View":
            self.btn_map.setText("Map")
            self.stackedWidget.setCurrentIndex(0)

    def update_slots(self):
        for i, camera_url in enumerate(self.threads):
            if self.threads[i] not in self.modified:
                if self.translate:
                    camera_label = QLabel(f"카메라 {i+1}")
                else:
                    camera_label = QLabel(f"Camera No : {i+1}")
                self.btn_addr.append(camera_label)
                self.gridLayout_4.addWidget(camera_label, i, 0)
                if self.translate:
                    modify_button = QPushButton("수정하다")
                else:
                    modify_button = QPushButton("Modify Slot")
                modify_button.setObjectName(str(i)) 
                modify_button.clicked.connect(partial(self.update_button_color,i))
                modify_button.setStyleSheet("background-color: red;")
                self.gridLayout_4.addWidget(modify_button, i, 1)

    def is_rtsp_live(self,rtsp_url):
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            return False
        _, frame = cap.read()
        cap.release()
        if frame is None:
            return False
        return True

    def update_button_color(self,i):
        button = self.sender()  # Get the button that triggered the slot
        button_index = int(button.objectName())
        thread_id = i
        if button.styleSheet() == "background-color: red;":
            
            camera = session.query(Camera).filter_by(camera_id=thread_id+1).first()
            if self.is_rtsp_live(camera.ip_address)==True:
                button.setStyleSheet("background-color: green;")

                showRedraw = RedrawSlot(thread_id,camera.camera_name,camera.ip_address,camera.username,camera.password)
                dialog = QDialog()

                #--------------------------------------------------
                # dialog.setWindowFlags(Qt.FramelessWindowHint)
                if self.translate:
                    dialog.setWindowTitle("주차 공간 그리기")
                else:
                    dialog.setWindowTitle("Draw ROI")
                dialog.setLayout(QVBoxLayout())
                dialog.layout().addWidget(showRedraw)
                dialog.exec_()

                self.threads[thread_id] = cores.thread.ThreadVideo(self, camera.ip_address, thread_id)#,self.model)
                self.threads[thread_id].imgSignal.connect(self.getImg)
                self.threads[thread_id].threadactive = True
                self.threads[thread_id].setTerminationEnabled(True)
                self.threads[thread_id].start()
                self.modified.append(self.threads[thread_id])

                self.btn_addr[thread_id].setVisible(False)
                button.setVisible(False)
            else:
                if self.translate:
                    QMessageBox.information(self, "경고", "카메라 연결이 끊어졌습니다")
                else:
                    QMessageBox.information(self, "Warning", "Camera is Disconnected")                
        else:
            button.setStyleSheet("background-color: red;")

        for i in range(self.frame_modify.layout().count()):
            item = self.frame_modify.layout().itemAt(i)
            if item.widget() and isinstance(item.widget(), QPushButton):
                if item.widget().styleSheet() == "background-color: green;":
                    break
        #self.widget_devicemgr.setVisible(False)

    def add_db(self):
        DeviceName = self.deviceName.text()
        IP = self.add_ip.text()
        UserName = self.add_username.text()
        Password = self.add_password.text()
        location = self.add_location.text()

        if DeviceName != "" and IP != "" and UserName != "" and Password != "" and location != "":
            if self.is_rtsp_live(IP)==True:
                self.draw(DeviceName,IP,UserName,Password,location)
            else:
                if self.translate:
                    QMessageBox.information(self, "경고", "카메라 연결이 끊어졌습니다")
                else:
                    QMessageBox.information(self, "Warning", "Camera is Disconnected")                  
            # self.new_count+=1
            # self.update_slots()
        else:
            self.msg = QMessageBox()
            self.msg.setIcon(QtWidgets.QMessageBox.Critical)
            if self.translate:
                self.msg.setInformativeText("잘못된 정보입니다!")
                self.msg.setWindowTitle("오류")
            else:
                self.msg.setInformativeText("Invalid Information!")
                self.msg.setWindowTitle("Error")
            self.msg.exec_()
            return
        
    def draw(self,DeviceName,IP,UserName,Password,location): 
        id_cam = len(self.cam_links_draw)
        x = drawWidget(id_cam,DeviceName,IP,UserName,Password,location) #index,cam_link
        dialog = QDialog()
        #--------------------------------------------------
        # dialog.setWindowFlags(Qt.FramelessWindowHint)

        if self.translate:
            dialog.setWindowTitle("주차 공간 그리기")
        else:
            dialog.setWindowTitle("Draw Slots")
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(x)
        dialog.exec_()

        self.new_rtsp = cores.thread.ThreadVideo(self, IP, id_cam)#,self.model)
        self.cam_links_draw.append(IP)
        self.new_rtsp.imgSignal.connect(self.getImg)
        self.new_rtsp.setTerminationEnabled(True)
        self.new_rtsp.start()
        self.threads.append(self.new_rtsp)

        self.newAdded= True
        self.deviceName.clear()
        self.add_ip.clear()
        self.add_username.clear()
        self.add_password.clear()
        #self.widget_devicemgr.setVisible(False)

        if len(self.threads)>32:
            self.cam64()
        elif len(self.threads)>16:
            self.cam32()
        elif len(self.threads)>8:
            self.cam16()
        elif len(self.threads)>4:
            self.cam8()
        elif len(self.threads)>1:
            self.cam4()
        else:
            self.cam1()


    def clear_db(self):
        self.killThread()
        try:
            shutil.rmtree("static")
            shutil.rmtree(f"{full_frame_path}")
        except Exception as e:
            print(e)
        try:
            delete_all_data()
        except Exception as e:
            print(e)
        #self.widget_devicemgr.setVisible(False)
        if self.translate:
            QMessageBox.information(self, "경고", "연결된 카메라가 모두 지워졌습니다. 관리자 권한으로 애플리케이션을 다시 실행하십시오.")
        else:
            QMessageBox.information(self, "Warning", "All the Connected Cameras are Cleared.Please Run the Application Again as Administrator")
        QApplication.quit()

    def showLukao(self):
        self.widget_devicemgr.setVisible(False)
    def showaddCamera(self):
        if self.widget_devicemgr.isVisible():
            self.widget_devicemgr.setVisible(False)
        else:
            self.widget_devicemgr.setVisible(True)

    def selectionChange(self,index,selected_analytics): #Analytics Select
            lst = [selected_analytics,index]
            cam_link = self.cam_links[index]

    def showDeviceMgr(self):
        self.device = Device_Manager()
        self.device.show()

    def showAbout(self):
        self.about = About()
    
    def showConfig(self):
        self.config = ConfigApp()
        self.config.show()
  
    def sizeHint(self):
        return QSize(width, height)

    def resizeEvent(self, event):
        self.update()

    @pyqtSlot(np.ndarray, int, bool)
    def getImg(self, img, index, active):
        self.actives[index] = active
        if active:
            self.img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
            self.labels[index].setPixmap(QPixmap(self.img).scaled(self.labels[index].size(), Qt.KeepAspectRatio, Qt.FastTransformation) )
            if index == self.newWindow.index:
                self.newWindow.lbl_cam.setPixmap(QPixmap.fromImage(self.img))
        else:
            # clear the label
            self.labels[index].clear()
            if index == self.newWindow.index:
                self.newWindow.close()

    def showSystem(self):
        for index, (self.lbl_cam, active) in enumerate(zip(self.labels, self.actives)):
            if not active:
                if self.translate:
                   text_ = "카메라가 {}\n연결되지 않았습니다!".format(index+1)
                else:
                    text_ = "CAMERA {}\nNOT CONNECTED!".format(index+1) 

                self.lbl_cam.setText(text_)

    def showCam(self, index):
        self.newWindow.index = index
        if not self.actives[index]:
            if self.translate:
                text_ = "카메라가 {}\n연결되지 않았습니다!".format(index+1)
            else:
                text_ = "CAMERA {}\nNOT CONNECTED!".format(index+1) 
            self.newWindow.lbl_cam.setText(text_)
        self.newWindow.setWindowTitle('CAMERA {}'.format(index+1))
        self.newWindow.resize(1000,600)
        #self.newWindow.show()
        self.newWindow.showMaximized()

    def recordCamera(self,index,obj,recObj):  # Record Function
        if obj.isChecked(): 
            obj.setIcon(QIcon(":/icon/icon/rec_recording.ico"))
            # recObj._record = True
        else: 
            obj.setIcon(QIcon(":/icon/icon/rec_normal.ico"))      	
            # recObj._record = False

            
    def cam1(self):
        try:
            self.layout.itemAt(0).widget().setVisible(True)
        except:
            self.show_error_msg()            
        try:
            for i in range(1,64):
                self.layout.itemAt(i).widget().setVisible(False)
        except:
            pass
    def cam4(self):
        try:
            for i in range(0,4):
                self.layout.itemAt(i).widget().setVisible(True)
        except:
           
            self.show_error_msg()
        
        try:
            for i in range(4,64):
                self.layout.itemAt(i).widget().setVisible(False)
        except:
            pass
    def cam8(self):
        try:
            for i in range(0,8):
                self.layout.itemAt(i).widget().setVisible(True)
        except:
           
            self.show_error_msg()
        
        try:
            for i in range(8,64):
                self.layout.itemAt(i).widget().setVisible(False)
        except:
            pass
    def cam16(self):
        try:
            for i in range(0,16):
                self.layout.itemAt(i).widget().setVisible(True)
        except:
           
            self.show_error_msg()
        
        try:
            for i in range(16,64):
                self.layout.itemAt(i).widget().setVisible(False)
        except:
            pass                 
    def cam32(self):
        try:
            for i in range(0,32):
                self.layout.itemAt(i).widget().setVisible(True)
        except:
           
            self.show_error_msg()
        
        try:
            for i in range(32,64):
                self.layout.itemAt(i).widget().setVisible(False)
        except:
            pass             
    def cam64(self):
        try:
            for i in range(0,64):
                self.layout.itemAt(i).widget().setVisible(True)
        except:
           
            self.show_error_msg()
        
        try:
            for i in range(64,64):
                self.layout.itemAt(i).widget().setVisible(False)
        except:
            pass 

    def retranslateUi(self):
        self.setWindowTitle("GK AI VMS - 라이브 뷰")
        self.label_2.setText("")
        self.label.setText("AI 스마트 주차 시스템")
        self.btn_home.setText("홈")
        self.btn_camera_add.setText("카메라 추가")
        self.btn_config.setText("설정")
        self.btn_about.setText("정보")
        self.label_3.setText("장치 관리자")
        self.label_6.setText("장치 이름")
        self.label_7.setText("IP")
        self.label_8.setText("사용자 이름")
        self.label_9.setText("비밀번호")
        self.btn_add.setText("추가")
        self.btn_lukao.setText(">")
        self.label_10.setText("슬롯 업데이트")
        self.btn_devicemgr.setText("장치 관리자")
        # If tooltip, status tip, and what's this text were not translated, they can remain as they are.
        self.btn_cleardb.setToolTip("<html><head/><body><p>모든 비디오 닫기</p></body></html>")
        self.btn_cleardb.setStatusTip("")
        self.btn_cleardb.setWhatsThis("")
        self.btn_cleardb.setText("모든 카메라 지우기")
        self.line_All_CPU.setText("0")
        self.line_VMS_CPU.setText("0")
        self.label_All_CPU.setText("전체 CPU 상태    :")
        self.label_VMS_CPU.setText("VMS CPU 상태 :")
        self.label_Memory.setText("메모리 상태  :")
        self.line_Memory.setText("0")
        self.label_5.setText("")
        self.label_4.setText("저작권©2024, Group 04. 모든 권리 보유.")
    # retranslateUi

    def show_error_msg(self):
        if self.translate:
            QMessageBox.critical(self, "카메라 오류", "카메라가 부족합니다.")
        else:
            QMessageBox.critical(self, "Camera Error", "You don't have sufficient camera")


    def refreshThread(self): 
        self.cam_links = cameraConnect().LoadCam()
        self.killThread()  
        for i in self.threads:
            i.threadactive = True
            i.setTerminationEnabled(True)
            i.start()

    def killThread(self): 
        for i in self.threads:
            try:
                i.stop()
                # i.requestInterruption()
                if not i.finished():
                    i.wait()
                if i.requestInterruption():
                    i.terminate()
            except Exception as e:
                pass
                # print("Thread Kill Error: -> ",e)

    def closeEvent(self, event):
        # Show a confirmation dialog
        if self.translate:
            reply = QMessageBox.question(self, '메시지', "종료하시겠습니까?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.killThread()
            event.accept()

def delete_all_data():
    # Create an engine and session as you did in your original code
    engine = create_engine('sqlite:///parking.db')  # Adjust the database URL as needed
    Session = sessionmaker(bind=engine)
    session = Session()
    # Iterate through all tables and delete all rows
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    # Commit the transaction and close the session
    session.commit()
    session.close()




# import rec
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = Live_view()
    app.exec_()
