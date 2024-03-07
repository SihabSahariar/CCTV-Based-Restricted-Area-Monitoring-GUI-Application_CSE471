from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from functools import partial
from threading import Lock,Thread
import numpy as np
import time
import cv2
import os
import time
from Model.db import Model as DataBase
from camera_links import *
import pickle
from datetime import datetime
import csv
import face_recognition
import cvzone 
from queue import Queue
capture_delay = 100 

db = DataBase("./Model/databases/device_info.db")

class ThreadVideo(QThread):
	imgSignal = pyqtSignal(np.ndarray, int, bool,np.ndarray,bool,bool,str)

	def __init__(self, parent, cam_link, index):
		QThread.__init__(self, parent)
		self.lock = Lock()
		self.p = parent
		self.threadactive = True
		self.cam_link = cam_link
		self.index = index
		self.add_info   = []+(cameraConnect().LoadInfo())
		self.skip_frames = 5
		try:
			self.additional_info = "Location : " + self.add_info[index]
		except:
			self.additional_info = ""

		self.queue = Queue(maxsize=5)

	def read_frames(self):
		self.cap = cv2.VideoCapture(self.cam_link)
		self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 30)
		self.cap.set(cv2.CAP_PROP_FPS, 30)  # Set the desired frame rate
		while self.threadactive and self.queue.qsize()<=5:
		    # print(self.queue.qsize())
		    has, img = self.cap.read()
		    if not has:
		        self.cap.release()
		        break

		    if self.queue.full():
		        self.queue.get_nowait()

		    if self.cam_link==0:
		        scale_percent = 100 
		    else:
		        scale_percent = 70
		    width = int(img.shape[1] * scale_percent / 100)
		    height = int(img.shape[0] * scale_percent / 100)
		    dim = (width, height)
		    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
		    self.queue.put(img)

	def processFrame(self):
		c = 0
		while self.threadactive:
		    self.img = self.queue.get()
		    c = c + 1
		    if(c % self.skip_frames != 0):
		        continue

			# Process the frame for restricted area monitoring
	            		            
		    else:
		    	if self.additional_info:
		    		self.img = cv2.putText(self.img, self.additional_info, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 1, cv2.LINE_AA)
		    	self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
		    	self.imgSignal.emit(self.img, self.index, True,self.img,False,False,"")

		self.img = np.zeros((400,400,3), np.uint8)
		self.imgSignal.emit(self.img, self.index, False,self.img,False,False,"")

		self.cap.release()

	def run(self):
		x= Thread(target=self.read_frames)
		x.start()

		y = Thread(target=self.processFrame)
		y.start()

	def stop(self):
		try:
			self.threadactive = False
			cv2.destroyAllWindows()
			self.cap.release()	
		except:
			pass
