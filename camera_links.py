from Model.db import Model as DataBase

import pytest
from pytestqt import qtbot
db = DataBase("Model/databases/device_info.db")
class cameraConnect:
	def __init__(self):
		self.cameralist = []
		self.AddInfo = []

	def LoadCam(self):
		rawData = db.fetch()
		Data = list(rawData) 
		listData = []
		for i in Data:
			raw = list(i)
			if(raw[4]=="IP"):
				user,password,ip = raw[7],raw[8],raw[5]
				self.cameralist.append(ip)
			else:
				self.cameralist.append(raw[5])
		return self.cameralist

	def LoadInfo(self):
		rawData = db.fetch()
		Data = list(rawData) 
		listData = []
		for i in Data:
			raw = list(i)
			add_info = raw[2]
			self.AddInfo.append(add_info)
		return self.AddInfo
