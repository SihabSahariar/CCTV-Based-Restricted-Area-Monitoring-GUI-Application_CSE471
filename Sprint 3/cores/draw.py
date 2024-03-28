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


import configparser
config = configparser.ConfigParser()
config.read('config.ini')
translate = config.getboolean('I/O', 'translate')

full_frame_path = config['DEFAULT']['full_frame_dir']
db = DataBase()

def getScreenSize(height_scale = 2.25, width_scale = 3):
    from win32api import GetSystemMetrics
    Width =int(GetSystemMetrics(0)//width_scale)
    Height =int(GetSystemMetrics(1)//height_scale)
    return [Width,Height]
    
class Canvas(QtWidgets.QWidget):
    rectangle_added = QtCore.pyqtSignal(tuple)

    def __init__(self, index, cap, rect_occu_list,deviceName, cam_link, username, password, location):
        super().__init__()
        self.image_window_width,self.image_window_height = getScreenSize()[0],getScreenSize()[1] #640,480 #1040,720

        self.index = index

        self.deviceName = deviceName
        self.cam_link = cam_link
        self.username = username
        self.password = password
        self.location = location
        
        self.setFixedSize(self.image_window_width, self.image_window_height)
        # self.setFixedSize(640, 480)
        self.cap = cap
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.rect_list = [rct[0] for rct in rect_occu_list]
        self.undo_list = []
        self.redo_list = []

        self.rect_occu_list = rect_occu_list
        self.occupancy = ""
        self.loadFrame()
        self.cropped_folder = os.path.join(full_frame_path, f'Camera_{self.index}')
        print("Cropped Images Folder:",self.cropped_folder)
        os.makedirs(self.cropped_folder, exist_ok=True)



    def loadFrame(self):
        ret, frame = self.cap.read()
        #frame = cv2.resize(frame, (1024, 720))
        if ret:
            self.original_image = self.convert_frame(frame)
            self.update()
        else:
            self.update()

    def convert_frame(self, cv_img):
        height, width, bytesPerComponent = cv_img.shape
        bytesPerLine = bytesPerComponent * width
        cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB, cv_img)
        qimg = QImage(cv_img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        qpixmap = QPixmap(qimg)
        return qpixmap

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        image = self.original_image.toImage()
        scaled_image = image.scaled(
            self.rect().size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.x_scale = image.width() / self.image_window_width
        self.y_scale = image.height() / self.image_window_height

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
                    self.undo_list.append(("add", rect, True))
                elif selected_option == 0:
                    occupancy = False
                    self.occupancy = False
                    self.undo_list.append(("add", rect, False))

                rect_with_occupancy = (rect, occupancy)
                self.rect_list.append(rect)
                self.rect_occu_list.append([rect, occupancy])
                self.rectangle_added.emit(rect_with_occupancy)
                self.redo_list.clear()
                self.update()

            self.begin = QtCore.QPoint()
            self.end = QtCore.QPoint()

    def undo(self):
        if self.undo_list:
            action, rect, occupancy = self.undo_list.pop()
            if action == "add":
                self.rect_list.remove(rect)
                self.rect_occu_list.pop()
                if occupancy:
                    self.redo_list.append(("add", rect, True))
                else:
                    self.redo_list.append(("add", rect, False))
            elif action == "delete":
                self.rect_list.append(rect)
                self.rect_occu_list.append((rect, occupancy))
                if occupancy:
                    self.redo_list.append(("delete", rect, True))
                else:
                    self.redo_list.append(("delete", rect, False))
            self.update()

    def redo(self):
        if self.redo_list:
            action, rect, occupancy = self.redo_list.pop()
            if action == "add":
                self.rect_list.append(rect)
                self.rect_occu_list.append((rect, occupancy))
                if occupancy:
                    self.undo_list.append(("add", rect, True))
                else:
                    self.undo_list.append(("add", rect, False))
            elif action == "delete":
                self.rect_list.remove(rect)
                self.rect_occu_list.pop()
                if occupancy:
                    self.undo_list.append(("delete", rect, True))
                else:
                    self.undo_list.append(("delete", rect, False))

            self.update()

    def clear(self):
        self.rect_list.clear()
        self.undo_list.clear()
        self.redo_list.clear()
        self.rect_occu_list.clear()
        self.update()

    def save(self):
        sample_path = os.path.join(self.cropped_folder, f"Camera_{self.index}.png")
        self.original_image.save(sample_path)
        print(sample_path)
        lst_slots_info = []
        new_camera = Camera(camera_name=self.deviceName, ip_address=self.cam_link, username=self.username, password=self.password,location=self.location,\
                            sample_image_path=sample_path,numbers_of_slot= len(self.rect_list), created_at = datetime.now(), \
                                updated_at=datetime.now())
        session.add(new_camera)
        session.flush()

        cam_id = new_camera.camera_id
        new_list = []


        for i, (rect, occ) in enumerate(self.rect_occu_list):
            x1 = int(rect.x() * self.x_scale)
            y1 = int(rect.y() * self.y_scale)
            w = rect.width() * self.x_scale
            h = rect.height() * self.y_scale
            
            x2 = int(x1) + int(w)
            y2 = int(y1) + int(h)
            new_list.append((x1, y1, x2, y2))
            
            slot_no = i
            occupancy_status = occ

            cropped_image = self.original_image.copy(int(x1), int(y1), int(w), int(h))
            save_path = f"static/Images/Camera_{self.index}/Slot_{i}"
            pickle_path = f"static/pickles/Camera_{self.index}"
            occupancy_path = f"static/pickles/Camera_{self.index}"

            os.makedirs(save_path, exist_ok=True)
            os.makedirs(pickle_path, exist_ok=True)
            os.makedirs(occupancy_path, exist_ok=True)
            cropped_image.save(save_path+"/current.png")
            new_Cordinates = Coordinates(x1=x1, y1=y1, x2=x2, y2=y2)
            session.add(new_Cordinates)
            session.flush()
            coordinate_id = new_Cordinates.coordinates_id
            
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


        # session.add_all(lst_slots_info)
        session.commit()

        # Save the updated occupancy status in the pickle file
        with open(pickle_path+"/slots", 'wb') as f:
            pickle.dump(self.rect_occu_list, f)

        print(self.rect_occu_list)
        self.msg = QMessageBox()
        self.msg.setIcon(QtWidgets.QMessageBox.Information)
        if translate:
            self.msg.setInformativeText("정보가 저장되었습니다!")
            self.msg.setWindowTitle("저장됨")
        else:
            self.msg.setInformativeText("Information Saved!")
            self.msg.setWindowTitle("Saved")
        self.msg.exec_()
        self.window().close()
        
        

class RectangleInfoWidget(QtWidgets.QWidget):
    def __init__(self, rect_occu_list):
        super().__init__()
        self.rect_occu_list_widget = rect_occu_list
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        if translate:
            self.table_widget.setHorizontalHeaderLabels(["슬롯", "점유율"])
        else:
            self.table_widget.setHorizontalHeaderLabels(["Slot", "Occupancy"])
        self.table_widget.setMaximumWidth(300)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout = QVBoxLayout()
        x = QLabel("Slot List")
        x.setStyleSheet("background-color: rgb(42, 54, 159);color:white;")
        x.setAlignment(Qt.AlignCenter)
        layout.addWidget(x)
        layout.addWidget(self.table_widget)
        self.setLayout(layout)
        if len(self.rect_occu_list_widget) > 0:
            for rct in self.rect_occu_list_widget:
                self.add_row(rct[0] + 1, rct[1])
            for i in range(len(self.rect_occu_list_widget)):
                self.table_widget.item(i, 1).setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )

        self.table_widget.cellDoubleClicked.connect(self.changeOccupancyState)
        self.deleted_rect_items = []

    def changeOccupancyState(self, row, column):
        if column == 1:
            item = self.table_widget.item(row, column)
            if item.text() == "Unoccupied":
                self.rect_occu_list_widget[row][1] = True
                item.setText("Occupied")
                item.setForeground(QtCore.Qt.white)
                item.setBackground(QtCore.Qt.red)
            else:
                item.setText("Unoccupied")
                item.setForeground(QtCore.Qt.white)
                item.setBackground(QtCore.Qt.darkGreen)
                self.rect_occu_list_widget[row][1] = False

    def add_row(self, rct):
        sno = self.table_widget.rowCount()
        self.table_widget.insertRow(sno)
        occupancy = rct[1]
        occu_text = "Occupied" if occupancy else "Unoccupied"
        if translate:
            slot_item = QTableWidgetItem(str(f"슬롯: {sno+1}"))
        else:
            slot_item = QTableWidgetItem(str(f"Slot: {sno+1}"))
        occu_item = QTableWidgetItem(occu_text)
        if occupancy:
            occu_item.setForeground(QtCore.Qt.white)
            occu_item.setBackground(QtCore.Qt.red)
        else:
            occu_item.setForeground(QtCore.Qt.white)
            occu_item.setBackground(QtCore.Qt.darkGreen)
        self.table_widget.setItem(sno, 0, slot_item)
        self.table_widget.setItem(sno, 1, occu_item)

    def add_rectangle(self, rect_with_occupancy):
        self.add_row(rect_with_occupancy)

    def remove_rectangle(self):
        deleted_row = []
        if self.table_widget.rowCount() > len(self.rect_occu_list_widget):
            for i in range(self.table_widget.columnCount()):
                deleted_row.append(
                    self.table_widget.takeItem(self.table_widget.rowCount() - 1, i)
                )
            self.deleted_rect_items.append(deleted_row)
            self.table_widget.removeRow(self.table_widget.rowCount() - 1)

    def redo_last_deleted_item(self):
        if self.deleted_rect_items:
            deleted_item = self.deleted_rect_items.pop()
            row_index = self.table_widget.rowCount()
            self.table_widget.insertRow(row_index)
            for column_index, item in enumerate(deleted_item):
                table_item = QTableWidgetItem(item.text())
                self.table_widget.setItem(row_index, column_index, table_item)


class drawWidget(QWidget):
    def __init__(self, index,DeviceName, IP, UserName, Password,location):
        super(drawWidget, self).__init__()
        self.index = index
        self.deviceName = DeviceName
        self.cam_link = IP
        self.username = UserName
        self.password = Password
        self.location = location
        
        self.cap = cv2.VideoCapture(self.cam_link)
        # self.setStyleSheet(open("style.qss").read())
        self.setStyleSheet("""

            QLabel {
                background-color: rgba(11, 161, 235,255);
                color: white;
            }

            QPushButton {
                background-color: rgba(11, 161, 235,255);
                color: white;
                border: none;
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
        try:
            with open(f"modules/pickle/pickle_{self.index}", "rb") as f:
                rect_occu_list = pickle.load(f)
        except:
            rect_occu_list = []
        self.canvas = Canvas(self.index, self.cap, rect_occu_list, self.deviceName, self.cam_link, self.username, self.password, self.location)

        self.rectangle_info_widget = RectangleInfoWidget(rect_occu_list)

        self.button_widget = QWidget()
        self.undo_button = QPushButton("Undo")

        self.reload_button = QPushButton("Change Frame")
        self.reload_button.clicked.connect(self.canvas.loadFrame)
        self.undo_button.clicked.connect(self.canvas.undo)
        self.undo_button.clicked.connect(self.rectangle_info_widget.remove_rectangle)
        self.redo_button = QPushButton("Redo")
        self.redo_button.clicked.connect(self.canvas.redo)
        self.redo_button.clicked.connect(
            self.rectangle_info_widget.redo_last_deleted_item
        )
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.canvas.clear)
        self.clear_button.clicked.connect(self.clear_canvas)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.canvas.save)
        # self.save_button.clicked.connect(self.clear_canvas)
        buttons = [
            self.reload_button,
            self.undo_button,
            self.redo_button,
            self.clear_button,
            self.save_button,
        ]
        if translate:
            self.reload_button.setText("프레임 변경")
            self.undo_button.setText("되돌리기")
            self.redo_button.setText("다시하기")
            self.clear_button.setText("지우기")
            self.save_button.setText("저장")

        for i in buttons:
            i.setMinimumSize(100, 40)
            i.setMaximumSize(100, 40)
        hbox = QHBoxLayout()
        hbox.addWidget(self.reload_button)
        hbox.addWidget(self.undo_button)
        hbox.addWidget(self.redo_button)
        hbox.addWidget(self.clear_button)
        hbox.addWidget(self.save_button)
        self.button_widget.setLayout(hbox)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas, 1)
        # vbox.addWidget(self.image_label, 4)

        hbox2 = QHBoxLayout()
        hbox2.addLayout(vbox)
        hbox2.addWidget(self.rectangle_info_widget)

        vbox2 = QVBoxLayout()
        vbox2.addLayout(hbox2)
        vbox2.addWidget(self.button_widget)
        self.setLayout(vbox2)

        self.canvas.rectangle_added.connect(self.on_rectangle_added)
        # self.show()

    def on_rectangle_added(self, rect_with_occupancy):
        self.rectangle_info_widget.add_rectangle(rect_with_occupancy)

    def clear_canvas(self):
        self.canvas.rect_list.clear()
        self.canvas.undo_list.clear()
        self.canvas.redo_list.clear()
        self.rectangle_info_widget.table_widget.clearContents()
        self.rectangle_info_widget.table_widget.setRowCount(0)
