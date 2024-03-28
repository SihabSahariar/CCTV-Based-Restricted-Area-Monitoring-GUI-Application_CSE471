# Developed By Sihab Sahariar
from db import DataBase
from database_setup import Camera,Slot,ReferenceImage,OccupancyHistory
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

db = DataBase()
class cameraConnect:
	def __init__(self):
		self.cameralist = []
		self.AddInfo = []
	def LoadCam(self):
		rawData = db.fetch()
		Data = list(rawData) 
		listData = []
		for i in Data:
			self.cameralist.append(i[2])

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
# x = cameraConnect()
# p = x.LoadCam()
# print(p)

