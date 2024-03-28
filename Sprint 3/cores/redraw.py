import sys
import pickle
import os
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtGui
os.environ["OPENCV_VIDEOIO_DEBUG"] = "0"
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(
    QLibraryInfo.PluginsPath
)
from database_setup import *
import cv2
from db import *
from detector.utils import draw_detections, check_overlap_and_percentage,putBText,draw_detections_bbox_nofill,draw_detections_bbox
from detector.YOLOv8 import YOLOv8

import configparser
config = configparser.ConfigParser()
config.read('config.ini')
translate = config.getboolean('I/O', 'translate')

full_frame_path = config['DEFAULT']['full_frame_dir']
db = DataBase()

parking_threshold = config.getfloat('THRESHOLDS', 'parking_threshold')
conf_thres = config.getfloat('THRESHOLDS', 'conf_thres')
iou_thres = config.getfloat('THRESHOLDS', 'iou_thres')
model_path = config['DEFAULT']['model_path']


def getScreenSize(height_scale = 2.25, width_scale = 3):
    from win32api import GetSystemMetrics
    Width =int(GetSystemMetrics(0)//width_scale)
    Height =int(GetSystemMetrics(1)//height_scale)
    print("Screen Size:",Width,Height)
    return [Width,Height]
    
class Canvas(QtWidgets.QWidget):
    rectangle_added = QtCore.pyqtSignal(tuple)
    def __init__(self, index, cap, rect_occu_list, deviceName, cam_link, username, password,occupancy_status_db):
        super().__init__()
        self.image_window_width,self.image_window_height = getScreenSize()[0],getScreenSize()[1] #640,480 #1040,720
        self.index = index
        self.deviceName = deviceName
        self.cam_link = cam_link
        self.username = username
        self.password = password
        self.occupancy_status_db = occupancy_status_db

        self.lst_slot_occupancy = []
        self.lst_detection_rect = []

        self.setFixedSize(self.image_window_width, self.image_window_height)
        # self.setFixedSize(640,480)1
        self.cap = cap
        self.rect_occu_list = rect_occu_list
        
        self.cropped_folder = os.path.join(full_frame_path, f'Camera_{self.index}')
        os.makedirs(self.cropped_folder, exist_ok=True)
        self.occupancy = ""
        # Add
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.rect_list = [rct[0] for rct in rect_occu_list]

        self.loadFrame()


    def loadFrame(self):
        ret, frame = self.cap.read()
        if ret:
            self.original_image = self.convert_frame(frame)
            self.update()
            self.get_ai_occupancy()
        else:
            self.update()
        
    def convert_frame(self, cv_img):
        model = YOLOv8(model_path,conf_thres=conf_thres,iou_thres=iou_thres)
        self.boxes, scores, class_ids = model(cv_img.copy())

        height, width, bytesPerComponent = cv_img.shape
        bytesPerLine = bytesPerComponent * width
        cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB, cv_img)
        qimg = QImage(cv_img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        qpixmap = QPixmap(qimg)        
        return qpixmap

    def get_ai_occupancy(self):
        # Draw the rectangles using AI
        ai_occu_list = []
        image = self.original_image.toImage()
        x =  image.width()/self.image_window_width 
        y =  image.height()/self.image_window_height 
        for i in range(len(self.boxes)):
            
            box = self.boxes[i]
            x1 = int(box[0]/x)
            y1 = int(box[1]/y)
            x2 = int(box[2]/x)
            y2 = int(box[3]/y)
            rect = QtCore.QRect(x1, y1, x2-x1, y2-y1)
            self.lst_detection_rect.append(rect)

        
        # for i, rect in enumerate(self.rect_occu_list):
        #     overlapped = False
        #     qrect = QtCore.QRect(
        #             int(rect[0].x()), int(rect[0].y()), int(rect[0].width()), int(rect[0].height())
        #         )
        #     for j, item in enumerate(self.lst_detection_rect):
                
        #         if item.intersects(qrect):
        #             overlapped = True
        #             break  
        #     ai_occu_list.append(overlapped)      
                
        MIN_OVERLAP_RATIO = 0.2  # Minimum overlap ratio (20%)

        for i, rect in enumerate(self.rect_occu_list):
            overlapped = False
            qrect = QtCore.QRect(
                int(rect[0].x()), int(rect[0].y()), int(rect[0].width()), int(rect[0].height())
            )
            for j, item in enumerate(self.lst_detection_rect):
                intersection = qrect.intersected(item).normalized()
                area_intersection = intersection.width() * intersection.height()
                area_rect = qrect.width() * qrect.height()

                if area_intersection / area_rect >= MIN_OVERLAP_RATIO:
                    overlapped = True
                    break

            ai_occu_list.append(overlapped)

        return ai_occu_list

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        image = self.original_image.toImage()
        scaled_image = image.scaled(
            self.rect().size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.x_scale = image.width() / self.image_window_width
        self.y_scale = image.height() / self.image_window_height
        # print(self.x_scale, self.y_scale)
        qp.drawImage(self.rect(), image)
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255), 2)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 10, 100))
        qp.setPen(pen)
        qp.setBrush(brush)

        for index, rect in enumerate(self.rect_list):
            qp.drawRect(rect)
            label_text = str(index+1)
            font_metrics = QtGui.QFontMetrics(qp.font())
            label_width = font_metrics.width(label_text)
            label_height = font_metrics.height()
            label_rect = QtCore.QRectF(
                rect.center().x() - label_width / 2,
                rect.center().y() - label_height / 2,
                label_width,
                label_height,
            )
            if self.occupancy:
                qp.drawText(label_rect, 5, label_text)
            else:
                qp.drawText(label_rect, 5, label_text)


        if self.begin and self.end:
            qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.begin = event.pos()
            self.end = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            rect = QRectF(self.begin, self.end)
            startPoint = (self.begin.x(), self.begin.y())
            endPoint = (self.end.x(), self.end.y())

            if rect.width() > 0 and rect.height() > 0:
                # Create a message box for selecting an option
                msg_box = QMessageBox()

                if translate:
                    msg_box.setWindowTitle("옵션 선택")
                    msg_box.setText("옵션을 선택하세요:")

                    msg_box.addButton("비어 있음", QMessageBox.NoRole)
                    msg_box.addButton("점유됨", QMessageBox.YesRole)
                    msg_box.addButton("닫기", QMessageBox.RejectRole)
                else:
                    msg_box.setWindowTitle("Select Option")
                    msg_box.setText("Choose an option:")

                    msg_box.addButton("Unoccupied", QMessageBox.NoRole)
                    msg_box.addButton("Occupied", QMessageBox.YesRole)
                    msg_box.addButton("Close", QMessageBox.RejectRole)

                # Show the message box and get the selected option
                selected_option = msg_box.exec()

                if selected_option == 2:
                    print("cancel")
                    return

                # Add the selected option and rectangle to the undo list
                if selected_option == 1:
                    occupancy = True
                    self.occupancy = True
                elif selected_option == 0:
                    occupancy = False
                    self.occupancy = False

                rect_with_occupancy = (rect, occupancy)
                self.rect_list.append(rect)
                self.rect_occu_list.append([rect, occupancy])
                self.rectangle_added.emit(rect_with_occupancy)
                self.update()

            self.begin = QtCore.QPoint()
            self.end = QtCore.QPoint()
            # print(self.begin,self.end)

    def save(self,ai_check_box=None):
        session = Session()
        sample_path = os.path.join(self.cropped_folder, f'Camera_{self.index}.png')
        self.original_image.save(sample_path)
        slots = session.query(Slot).filter(Slot.camera_id == self.index+1).all()
        slot_id_lst = [int(slot.slot_id) for slot in slots]+[]
        itr = len(slot_id_lst)+1

        pickle_path = f"static/pickles/Camera_{self.index}"
        occupancy_path = f"static/pickles/Camera_{self.index}"

        print(len(self.rect_occu_list),len(ai_check_box),ai_check_box)
        for i, (rect, occ) in enumerate(self.rect_occu_list):
            try:
                occupancy_status = ai_check_box[i].isChecked()
                print("Saved",i,occupancy_status)
            except:
                occupancy_status = occ
                # print("Saved",i,occupancy_status)
            
            # occupancy_status = ai_occupancy_list[i]
            # Update the occupancy status in the database
            if i<len(slot_id_lst):
                slot_id = slot_id_lst[i]
                reference_image = session.query(ReferenceImage).filter_by(slot_id=slot_id).first()
                session.query(Slot).filter(Slot.slot_id == slot_id).update({"occupancy_status": occupancy_status})
                session.commit()

            x1 = int(rect.x() * self.x_scale)
            y1 = int(rect.y() * self.y_scale)
            w = rect.width() * self.x_scale
            h = rect.height() * self.y_scale
            x2 = int(x1) + int(w)
            y2 = int(y1) + int(h)
            cropped_image = self.original_image.copy(int(x1), int(y1), int(w), int(h))
            save_path = f"static/Images/Camera_{self.index}/Slot_{i}"

            # Create the directories if they don't exist
            os.makedirs(save_path, exist_ok=True)
            os.makedirs(pickle_path, exist_ok=True)
            os.makedirs(occupancy_path, exist_ok=True)
            
            cropped_image.save(save_path+"/current.png")
            # print("Saved",save_path)
            
            if i>=len(slot_id_lst):
                #-----------------------------New Coordinates------------------------------------
                new_Cordinates = Coordinates(x1=x1, y1=y1, x2=x2, y2=y2)
                session.add(new_Cordinates)
                session.flush()
                coordinate_id = new_Cordinates.coordinates_id
                cam_id = self.index+1
                slot_no = itr
                
                # print(new_Cordinates.coordinates_id)
                new_Slot = Slot(camera_id = cam_id,slot_number=slot_no, \
                                        occupancy_status=occupancy_status,coordinates_id=coordinate_id)
                session.add(new_Slot)
                session.flush()
                slot_id = new_Slot.slot_id
                new_Reference_Image = ReferenceImage(slot_id=slot_id,image_path=save_path,last_updated=datetime.now(), ref_img_occupancy=occupancy_status)
                session.add(new_Reference_Image)
                session.flush()
                if occupancy_status:
                    new_occupancy_history = OccupancyHistory(slot_id=slot_id,entry_time=datetime.now()) 
                    session.add(new_occupancy_history)
                    session.flush()
                itr+=1
                #---------------------------------------------------------------------------------

            # If a record with the given slot_id exists, update its ref_img_occupancy attribute
            if reference_image:
                reference_image.ref_img_occupancy = occupancy_status
                # print("Updated",occupancy_status)
                session.commit()

        # session.add_all(lst_slots_info)
        session.commit()
        # Save the updated occupancy status in the pickle file
        pickle_path = f"static/pickles/Camera_{self.index}"
        with open(pickle_path+"/slots", 'wb') as f:
            pickle.dump(self.rect_occu_list, f)

        self.msg = QMessageBox()
        self.msg.setIcon(QtWidgets.QMessageBox.Information)
        if translate:
            self.msg.setText("슬롯 변경 사항이 저장되었습니다!")
            self.msg.setWindowTitle("저장됨")
        else:
            self.msg.setInformativeText("Slot Changes are saved!")
            self.msg.setWindowTitle("Saved")

        self.msg.exec_()
        self.window().close()

class RectangleInfoWidget(QtWidgets.QWidget):
    def __init__(self, rect_occu_list,occupancy_status_db,lst_slot_occupancy):
        super().__init__()
        self.rect_occu_list_widget = rect_occu_list
        self.occupancy_status_db = occupancy_status_db
        self.lst_slot_occupancy = lst_slot_occupancy
        # print("Rect Occupied List",self.lst_slot_occupancy)

        layout = QVBoxLayout()
        self.check_boxes = []
        for i, (rect, occ) in enumerate(self.rect_occu_list_widget):

            slot_layout = QHBoxLayout()
            if translate:
                slot_label = QLabel(f"슬롯: {i+1}")
                slot_check_box = QCheckBox(u"점유됨")
            else:
                slot_label = QLabel(f"Slot: {i+1}")
                slot_check_box = QCheckBox("Occupied")

            slot_check_box.setChecked(self.occupancy_status_db[i])
            slot_check_box.stateChanged.connect(lambda state, i=i: self.on_checkbox_state_changed(state, i))
            self.check_boxes.append(slot_check_box)
            slot_layout.addWidget(slot_label)
            slot_layout.addWidget(slot_check_box)
            layout.addLayout(slot_layout)

        self.setLayout(layout)

    def on_checkbox_state_changed(self, state, index):
        self.rect_occu_list_widget[index] = (self.rect_occu_list_widget[index][0], state == Qt.Checked)

class RedrawSlot(QWidget):
    def __init__(self, index, DeviceName, IP, UserName, Password):
        super(RedrawSlot, self).__init__()
        self.index = index
        self.deviceName = DeviceName
        self.cam_link = IP
        self.username = UserName
        self.password = Password
        pickle_path = f"static/pickles/Camera_{self.index}"
        os.makedirs(pickle_path, exist_ok=True)

        # Load the camera feed and initialize the rectangle occupancy list
        self.cap = cv2.VideoCapture(self.cam_link)
        try:
            with open(pickle_path + "/slots", "rb") as f:
                self.rect_occu_list = pickle.load(f)
                # print("Load From DB:",self.rect_occu_list)
            self.occupancy_status_db = self.get_occupancy_status(self.index+1)
            print("Occupancy Status DB:",self.occupancy_status_db)
        except:
            self.rect_occu_list = []
        # print(self.rect_occu_list)
        self.canvas = Canvas(self.index, self.cap, self.rect_occu_list, self.deviceName, self.cam_link, self.username, self.password,self.occupancy_status_db)
        self.occupancy_status_db = Canvas.get_ai_occupancy(self.canvas)
        # print("Occupancy Status AI:",self.occupancy_status_db)
        # Wrap the RectangleInfoWidget in a QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.rectangle_info_widget = RectangleInfoWidget(self.rect_occu_list,self.occupancy_status_db,self.canvas.lst_slot_occupancy)
        self.scroll_area.setWidget(self.rectangle_info_widget)

        self.button_widget = QWidget()

        self.save_button = QPushButton("Save")
        self.reload_button = QPushButton("Reload Camera")
        self.save_button.clicked.connect(lambda:self.canvas.save(self.rectangle_info_widget.check_boxes))
        self.reload_button.clicked.connect(self.reload_camera)
        if translate:
            self.reload_button.setText("프레임 변경")
            self.save_button.setText("저장")

        buttons = [self.save_button, self.reload_button]
        for i in buttons:
            i.setMinimumSize(200, 40)
            i.setMaximumSize(200, 40)

        left_layout = QVBoxLayout()
        x = QLabel("Slot List")
        if translate:
            x.setText("주차 슬롯 목록")
            
        x.setStyleSheet("background-color: rgb(0, 128, 128);color:white;")
        x.setAlignment(Qt.AlignCenter)
        x.setFixedSize(300, 30)
        left_layout.addWidget(x)

        # Add the QScrollArea instead of the RectangleInfoWidget
        left_layout.addWidget(self.scroll_area)
        #left_layout.addStretch(1)
        left_layout.addWidget(self.save_button, alignment=Qt.AlignCenter)
        left_layout.addWidget(self.reload_button, alignment=Qt.AlignCenter)

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(left_layout)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 2)

        # Apply styling to the main widget
        self.setStyleSheet("""

            QLabel {
                background-color: rgba(11, 161, 235,255);
                color: white;
                padding: 5px;
            }

            QPushButton {
                background-color: rgba(11, 161, 235,255);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(11, 161, 235, 200);
            }
            QPushButton:pressed {
                background-color: rgba(11, 161, 235, 150);
            }
        """)

        # Set the minimum size of the main widget based on the image window size
        # self.setFixedSize(self.canvas.image_window_width+320, self.canvas.image_window_height)

        getScreenSize()

    def reload_camera(self):
        # Release the current camera and reload a new one
        self.cap.release()
        self.cap = cv2.VideoCapture(self.cam_link)
        self.canvas.cap = self.cap
        self.canvas.loadFrame()

    def get_occupancy_status(self,camera_id):
        camera = session.query(Camera).filter(Camera.camera_id == camera_id).first()
        if camera is not None:
            occupancy_status_list = [slot.occupancy_status for slot in camera.slots]
            return occupancy_status_list
        else:
            return None