from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from functools import partial
from threading import Lock,Thread
import numpy as np
import time
import cv2
import os
from db import DataBase
from camera_links import *
from datetime import datetime
import time
from queue import Queue
from skimage.metrics import structural_similarity
from collections import deque
from cores.camera_occupancy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database_setup import Slot
from sqlalchemy import update
import configparser

import redis
import json
import base64
from PIL import Image
from io import BytesIO
from clean_redis import *
from redis_image_stream_processor import *
from cores.recorder import RecordingThread

from detector.utils import check_overlap_and_percentage,putBText,draw_detections_bbox_nofill 
from detector.YOLOv8 import YOLOv8

from boxmot import BYTETracker


config = configparser.ConfigParser()
config.read('config.ini')
save_img = config.getboolean('I/O', 'save_img')
db_insert = config.getboolean('I/O', 'db_insert')
enable_redis = config.getboolean('I/O', 'enable_redis')
enable_web = config.getboolean('I/O', 'enable_web')
redis_host_new = config['I/O']['redis_server'] 
redis_host = redis_host_new.split(":")[0]
redis_port = int(redis_host_new.split(":")[1])
video_record = config.getboolean('I/O', 'video_record')
save_updated_ref_img = config.getboolean('I/O', 'save_updated_ref_img')
# Create a redis client
if enable_redis:
	client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
	
conf_thres = config.getfloat('THRESHOLDS', 'conf_thres')
iou_thres = config.getfloat('THRESHOLDS', 'iou_thres')
full_frame_path = config['DEFAULT']['full_frame_dir']
current_script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = config['DEFAULT']['model_path']
print(model_path)
redis_transition = config.getboolean('I/O', 'redis_transition')

engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)

class ThreadVideo(QThread):
	imgSignal = pyqtSignal(np.ndarray, int, bool)

	def __init__(self, parent, cam_link, index):
		QThread.__init__(self, parent)
		self.lock = Lock()
		self.p = parent
		self.threadactive = True
		self.cam_link = cam_link
		self.index = index
		self.camera_id = index + 1

		self.occu = get_occupancy(self.camera_id)
		# print("Occupancy For Thread",self.occu)
		self.posList = get_positions(self.camera_id)
		# print("Position PosList",self.posList)
		self.number_of_slots = len(self.posList)
		#all slots last updated time list
		self.slots_last_updated = [time.time() for _ in range(self.number_of_slots)]
		self.max_update_time = int(config['DEFAULT']['max_update_time'])
		#print(len(self.slots_last_updated))
		self.add_info   = []+(cameraConnect().LoadInfo())
		self.skip_frames = int(config['DEFAULT']['skip_frame'])
		# self.record_size = tuple(map(int, config['DEFAULT']['record_size'].split(',')))
		self.record_size = eval(config['DEFAULT']['record_size'])
		self.recording_dir = config['DEFAULT']['recording_dir']
		# os.makedirs(self.recording_dir, exist_ok=True)
		try:
			self.additional_info = self.add_info[index]
		except:
			self.additional_info = ""
		self.queue = Queue(maxsize=30)
		self.cropped_folder = f'static/Images/Camera_{self.index}'
		self.save_full_frame = os.path.join(full_frame_path, f'Camera_{self.index}')
		# Set the maximum length of each queue
		self.maxlen = int(config['DEFAULT']['maxqueue'])



		self.record = [False] * self.number_of_slots

  
		self.is_recording = [False] * self.number_of_slots
		self.start_rec = [None] * self.number_of_slots
		self.recorded_frames = [[] for _ in range(self.number_of_slots)]
		self.recording_thread = [None] * self.number_of_slots
		self.count = [0] * self.number_of_slots
		self.update_count = [0] * self.number_of_slots

		self.rest_sleep = 0.1

		# self.model = YOLOv8('detector/yolov8m.onnx',conf_thres=conf_thres,iou_thres=iou_thres)
		self.model = YOLOv8(model_path,conf_thres=conf_thres,iou_thres=iou_thres)

		# Initialize ByteTracker
		self.tracker = BYTETracker(
			track_thresh=0.45,
			match_thresh=0.9,
			track_buffer=20,
			frame_rate=24,
		)


	def cv2_image_to_b64(self, cv2_image):
		pil_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
		pil_image = Image.fromarray(pil_image)
		buffered = BytesIO()
		pil_image.save(buffered, format="PNG")
		b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

		return b64_str
		
	def read_frames(self):
		self.cap = cv2.VideoCapture(self.cam_link)
		# self.cap.set(cv2.CAP_PROP_FPS, 20)  # Set the desired frame rate
		self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 45)
		
		self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
		fps = self.cap.get(cv2.CAP_PROP_FPS)
		if self.isInterruptionRequested():
			self.threadactive = False
			self.x_read.join()

		while self.threadactive and self.queue.qsize()<=30:
			try:
				has, img = self.cap.read()
			except:
				self.cap.release()
				has = False
				break
			if not has:
				self.cap.release()
				break
			if self.queue.full():
				self.queue.get_nowait()
			self.queue.put(img)

			# time.sleep(self.rest_sleep)
			

	def processFrame(self):
		c = 0
		if self.isInterruptionRequested():
			self.threadactive = False
			self.y_process.join()
		while self.threadactive:
			self.img = self.queue.get()
			c = c + 1
			if(c % self.skip_frames != 0):
				continue

			st = time.time()
			self.img = cv2.cvtColor(self.img,cv2.COLOR_BGR2RGB)
			self.img_raw = self.img.copy()
			boxes, scores, class_ids = self.model(self.img)


			############# Apply ByteTracker #############
			vehicle_modified = []
			for box,score,cls_id in zip(boxes,scores,class_ids):
				if score is not None:
					vehicle_modified.append([box[0],box[1],box[2],box[3],score,cls_id,])
			dets = np.array(vehicle_modified)
			tracks = self.tracker.update(dets, self.img)
			if len(tracks) > 0:
				xyxys = tracks[:, 0:4].astype("int")  # float64 to int
				ids = tracks[:, 4].astype("int")  # float64 to int
				confs = tracks[:, 5]	
				self.img,lst_track_id = draw_detections_bbox_nofill(self.img, xyxys, confs, class_ids,self.posList,ids)
				self.check_ROI_space(self.img, st,xyxys,self.img_raw,lst_track_id)
			#############################################
			else:
				# self.img = draw_detections_bbox_nofill(self.img, boxes, scores, class_ids,self.posList)
				# self.check_ROI_space(self.img, st,boxes,self.img_raw)
				self.imgSignal.emit(self.img, self.index, True)

			# time.sleep(self.rest_sleep)
		self.img = np.zeros((400,400,3), np.uint8)
		self.imgSignal.emit(self.img, self.index, False)
		# self.cap.release()

	def run(self):
		# self.x_read= Thread(target=self.read_frames)
		# self.x_read.start()
		# self.y_process = Thread(target=self.processFrame)
		# self.y_process.start()

		# use threadpool 
		self.x_read = QThreadPool()
		self.x_read.start(self.read_frames)
		self.y_process = QThreadPool()
		self.y_process.start(self.processFrame)

	def stop(self):
		try:
			self.threadactive = False
			self.cap.release()
			self.x_read.join()
			self.y_process.join()
		except:
			pass


	def check_ROI_space(self,img, st,boxes,img_raw,ids=None):
		session = Session()

		raw_img = img_raw.copy()

		self.no_occupied = 0
		self.no_unoccupied = 0
		self.no_transition = 0

		red = (255, 69, 0)
		blue = (0,91,200)
		green = (118,186,27)
		purple = (255,0,255)
		white = (255,255,255)
		black = (0,0,0)
		text_red = (236,45,1)

		# Only Detection - No RoI
		if len(self.posList)==0:
			self.imgSignal.emit(img, self.index, True)	
			return		

		for i, pos in enumerate(self.posList):
			slot_number = i
			slot_num = "Slot " + str(i + 1)
			x, y = pos[0], pos[1]
			x1, y1 = pos[2], pos[3]
			occ = self.occu[i]

			width, height = (x1 - x), (y1 - y)
			max_x, min_x = max(x, x1), min(x, x1)
			max_y, min_y = max(y, y1), min(y, y1)
						
			if len(boxes)!=0 and ids is not None:
				check_flag = check_overlap_and_percentage(self.posList,boxes.tolist())
				all_ids = ids.copy()
				if(check_flag[i] == False):
					color = green
					occupancy = False
				else:
					color = red
					occupancy = True
					if save_img:
						# if a new ID is detected, save the image
						# if all_ids[i] not in self.update_count:
						file_name = f'./detected_person/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
						# self.update_count[i] = all_ids[i]
						img_save_ready = img.copy()
						img_save_ready = cv2.rectangle(img_save_ready, (x, y), (x + width, y + height), color, 2)
						img_save_ready = self.draw_filled_rectangle(img_save_ready, x, y, width, height, color, opacity=0.4)
						cv2.imwrite(file_name, img_save_ready)
						if(db_insert):
						
							camera = session.query(Camera).filter_by(camera_id=self.camera_id).first()
							camera.updated_at = datetime.now()
							
							slot_id = (session.query(Slot.slot_id).join(Camera).filter(Camera.camera_id == self.camera_id).filter(Slot.slot_number == slot_number).first())[0]
							session.query(Slot).filter(Slot.slot_id == slot_id).update({"occupancy_status": occupancy})

							new_recorded_video = RecordedVideo(exit_video_path = file_name, created_at = datetime.now())
							session.add(new_recorded_video)
							# Flush the session to persist the changes and generate the recorded_video_id
							session.flush()

							session.commit()

						if enable_web:
							self.send_message(self.camera_id,slot_id, occupancy)
							
						# else:
						# 	self.update_count[i] = all_ids[i]
															
			if color == red:
				self.no_occupied+=1
			if color == blue:
				self.no_transition+=1
			if color == green:
				self.no_unoccupied+=1
				
			self.x = self.img.copy()

			self.x = cv2.rectangle(self.img, (x, y), (x + width, y + height), color, 2)
			self.x = self.draw_filled_rectangle(self.img, x, y, width, height, color, opacity=0.4)
			size = min([self.x.shape[1], self.x.shape[0]]) * 0.0006
			text_thickness = int(min([self.x.shape[1], self.x.shape[0]]) * 0.0015)
			(tw, th), _ = cv2.getTextSize(text=f"{slot_num}", fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=size, thickness=text_thickness)
			th = int(th * 1.2)
			# mid_height = self.x.shape[0] // 2
			# mid_width = self.x.shape[1] // 2
			self.x = cv2.rectangle(self.x, (x, y), (x + tw, y - th), color, -1)
			self.x = cv2.putText(self.x, slot_num , (x, y), cv2.FONT_HERSHEY_SIMPLEX, size, (0, 0, 0), text_thickness, cv2.LINE_AA)
 
			session.close()

		width = int(self.x.shape[1] * 100 / 100)
		height = int(self.x.shape[0] * 100 / 100)
		mid_width = int(self.x.shape[1] * 50 / 100)+50

		# self.draw_str(self.x, (mid_width-590, height-50), f"Occupied :  {self.no_occupied}",c = (43,64,215))
		# self.draw_str(self.x, (mid_width-300, height-50), f"Unoccupied :  {self.no_unoccupied}",c = (3,75,3))
		# self.draw_str(self.x, (mid_width+30, height-50), f"Transition :  {self.no_transition}",c = (121,0,2))
		# self.draw_str(self.x, (mid_width+330, height-50), f"Total :  {self.number_of_slots}",c = (24,117,255))

		scale_percent = 100
		width = int(img.shape[1] * scale_percent / 100)
		height = int(img.shape[0] * scale_percent / 100)
		dim = (width, height)
		self.x = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

		self.img = cv2.cvtColor(self.x,cv2.COLOR_BGR2RGB)
		self.imgSignal.emit(self.x, self.index, True)

	def draw_filled_rectangle(self,img, x, y, width, height, color, opacity=0.5):
		overlay = img.copy()
		fill_color = (color[0], color[1], color[2])  # OpenCV uses BGR instead of RGB
        
		t = cv2.rectangle(overlay, (x, y), (x + width, y + height), fill_color, -1)
		t = cv2.addWeighted(overlay, opacity, img, 1 - opacity, 0, img)
		return t 

	def preprocess_image_for_video_generation(self, raw_img, x, y, width, height, i):
		rgb_img = cv2.cvtColor(raw_img, cv2.COLOR_BGR2RGB)
		rgb_rect = cv2.rectangle(rgb_img, (x, y), (x + width, y + height), (255, 0, 0), 2)

		height_t = int(self.x.shape[0] * 100 / 100)
		mid_width_t = int(self.x.shape[1] * 50 / 100) + 50					
		rgb_rect = putBText(rgb_rect, f"Vehicle Exiting From Slot : {i+1} of Camera : {self.index+1}",\
		      mid_width_t - 300, height_t - 100, vspace = 7, hspace = 7, font_scale = 0.7, background_RGB = (255,255,255),\
				text_RGB = (0,0,0), font = cv2.FONT_HERSHEY_SIMPLEX, thickness = 2, alpha=0.3, gamma=1)
		rgb_rect = cv2.resize(rgb_rect, self.record_size)
		return rgb_rect
	


	def send_message(self,camera_id, slot_id, occupancy):
		channel = 'people_monitoring'
		message = {'camera_id':camera_id,'slot_id': slot_id, 'status': occupancy}
		message = json.dumps(message)
		client.publish(channel, message)
		print("Send to Redis")

	def draw_str(self,dst, target, s,c):
		font_size = 5.0
		x, y = target
		putBText(dst,s,x,y,vspace=10,hspace=10, font_scale=1.0,background_RGB=(255,255,255),text_RGB=c,font = cv2.FONT_HERSHEY_SIMPLEX,thickness = 3,alpha=0.1,gamma=1)

	def start_recording(self,i):
		self.is_recording[i] = True
		print("Started Recording")

	def stop_recording(self,i,output_file,recorded_frames):
		self.is_recording[i] = False
		self.recording_thread[i]= RecordingThread(output_file, recorded_frames)
		self.recording_thread[i].start()
		self.recorded_frames[i].clear()

	def save_frame(self, i, image):
		# Delete the previous images
		if os.path.exists(f'{self.save_full_frame}/Camera_{i}.png'):
			os.remove(f'{self.save_full_frame}/Camera_{i}.png')
		# Save the current image
		cv2.imwrite(f'{self.save_full_frame}/Camera_{i}.png', image)
		print(f"Saved at {self.save_full_frame}/Camera_{i}.png")


	def delete_all_images(self, dir):
		# Get a list of all files in the directory
		file_list = os.listdir(dir)

		# Loop through the files and delete the ones that are not "current.png"
		for filename in file_list:
			if filename != "current.png":
				file_path = os.path.join(dir, filename)
				if os.path.isfile(file_path):
					os.remove(file_path)


