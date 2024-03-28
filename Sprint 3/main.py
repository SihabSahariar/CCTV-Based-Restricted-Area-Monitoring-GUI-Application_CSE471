# Lynkeus AI VMS
# Developed By Sihab Sahariar

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QCursor
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from live_view import *
from PyQt5 import QtSql
import sys
import os
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'
os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(QLibraryInfo.PluginsPath)
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import configparser
config = configparser.ConfigParser()
config.read('config.ini')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        loadUi("Forms/login.ui",self)
        QShortcut(QtCore.Qt.Key_Enter, self, self.loginCheck)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.center()
        self.oldPos = self.pos()
        self.pushButton_2.clicked.connect(self.closeWindow)
        self.pushButton.clicked.connect(self.loginCheck)
        self.lineEdit_2.returnPressed.connect(self.loginCheck)
        self.lineEdit.returnPressed.connect(self.loginCheck)
        #self.movie = QMovie(":/icon/icon/Media1.gif")
        #self.gif.setMovie(self.movie)
        #self.movie.start()


        #################### Translation START ####################
        # Translate
        self.translate = config.getboolean('I/O', 'translate')
        if self.translate:
            self.retranslateUi()
        
        #################### Translation END ####################

    def retranslateUi(self):
        self.setWindowTitle("MainWindow")
        self.label.setText("")
        self.label_2.setText("")
        self.label_4.setText("로그인")
        self.lineEdit.setPlaceholderText("사용자 이름")
        self.lineEdit_2.setPlaceholderText("비밀번호")
        self.pushButton.setText("로그인")
        self.label_5.setText("AI 스마트 주차 시스템")
        self.pushButton_2.setText("종료")

    def loginCheck(self):
        if self.lineEdit.text()==query.value(0) and self.lineEdit_2.text()==query.value(1):
            self.ShowLiveView()
            self.close()
        else:
            if self.lineEdit_2.text()=="":
                self.lineEdit_2.setFocus()  
            if self.lineEdit.text()=="":
                self.lineEdit.setFocus()
              
            if self.translate:
                QMessageBox.critical(self, "실패", "로그인 실패")
            else:
                return QMessageBox.critical(self, "Failed", "Login Failed")

    def ShowLiveView(self):
        self.close() 
        self.live = Live_view()

    def center(self):
        ref = self.frameGeometry()
        place = QtWidgets.QDesktopWidget().availableGeometry().center()
        ref.moveCenter(place)
        self.move(ref.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    # Minimize window
    def hideWindow(self):
        self.showMinimized()

    # Close window
    def closeWindow(self):
        self.close()


def createConnection():
    global query
    con = QtSql.QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName("cores/databases/login.sqlite")
    if not con.open():
        QMessageBox.critical(
            None,
            "Database Error",
            "Database Error: %s" % con.lastError().databaseText(),
        )
        return False
    query = QtSql.QSqlQuery("select * from userdata")
    query.first()
    return True


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyleSheet(qdarktheme.load_stylesheet("light")) 
    if not createConnection():
        sys.exit(1)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
