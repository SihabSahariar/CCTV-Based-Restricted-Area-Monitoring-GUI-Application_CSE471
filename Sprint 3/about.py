# Developed By Sihab Sahariar
import sys
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
import configparser
config = configparser.ConfigParser()
config.read('config.ini')


class About(QWidget):
    def __init__(self):
        super(About,self).__init__()
        loadUi("Forms/about.ui",self)
        self.setWindowIcon(QIcon(":/icon/icon/dome_camera_80px.png")) 
        self.setWindowTitle("About")
        print("About")
        self.btn_okay.clicked.connect(self.close)
        # Distable the maximize button
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        # show in center screen
        qtRectangle = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        
        self.show()
        #################### Translation START ####################
        self.translate = config.getboolean('I/O', 'translate')
        
        # Translate
        if self.translate:
            self.retranslateUi()
        
        #################### Translation END ####################
    def retranslateUi(self):
        self.setWindowTitle(u"~에 대한")
        self.textBrowser.setHtml(u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'century gothic'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">\uc18c\ud504\ud2b8\uc6e8\uc5b4 \ubc0f AI \uc194\ub8e8\uc158 \uac1c\ubc1c\uc0ac : Lynkeus AI</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">\uc774\uba54\uc77c :info@lynkeus.kr</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">\ud648\ud398"
                        "\uc774\uc9c0 : https://lynkeus.kr/</span></p></body></html>")
        self.btn_okay.setText( u"\uc88b\uc544\uc694")
        self.label_3.setText("")
        self.label.setText( u"AI \uc2a4\ub9c8\ud2b8 \uc8fc\ucc28 \uc2dc\uc2a4\ud15c")
        self.label_4.setText( u"\uc800\uc791\uad8c\u00a92023, GK AI. \ud310\uad8c \uc18c\uc720.")
    # retranslateUi

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = About()
    window.show()
    app.exec_()