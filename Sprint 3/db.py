# Developed By Sihab Sahariar
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import *
from datetime import datetime
import warnings
from sqlalchemy import exc as sa_exc
warnings.filterwarnings("ignore", category=sa_exc.SAWarning)
# Data Field : device_name,additional_info,cam_group,login_type,ip,port,username,password,protocol
engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)
session = Session()

class DataBase:
    def fetch(self):
        cameras = session.query(Camera).all()
        lst_camera = []
        for camera in cameras:
            lst_camera.append([camera.camera_id, camera.camera_name, camera.ip_address, camera.username, camera.password,camera.location, camera.sample_image_path,\
                                camera.numbers_of_slot,camera.created_at, camera.updated_at])
        return lst_camera


    def insert(self, device_name, ip, username, password,location, sample_image="",slot_no=""):
        lastUpdate = datetime.now()
        new_camera = Camera(camera_name=device_name, ip_address=ip, username=username, password=password,location=location,\
                             sample_image_path=sample_image,numbers_of_slot = slot_no, last_updated=lastUpdate)
        session.add(new_camera)
        session.commit()
        return new_camera.camera_id

    def remove(self, ID):
        camera_to_remove = session.query(Camera).filter(Camera.camera_id == ID).first()
        if camera_to_remove:
            session.delete(camera_to_remove)
            session.commit()


    def update(self, ID, device_name, ip, username, password,location, sample_image,slot_no,lastUpdate):
        # Query the row you want to update based on a filter condition
        camera_to_update = session.query(Camera).filter(Camera.camera_id == ID).first()

        # Check if the row exists
        if camera_to_update:
            # Modify the attributes of the queried object with the new values
            camera_to_update.camera_id = ID
            camera_to_update.camera_name = device_name
            camera_to_update.ip_address = ip
            camera_to_update.username = username
            camera_to_update.password = password
            camera_to_update.location = location
            camera_to_update.sample_image_path = sample_image
            camera_to_update.numbers_of_slot = slot_no
            camera_to_update.last_updated = lastUpdate
            # Commit the changes to the session
            session.commit()

    def deleteExtraData(self):
        session.query(Coordinates).delete()
        session.query(Slot).delete()
        session.query(ReferenceImage).delete()
        session.query(OccupancyHistory).delete()
        session.commit()

    def __del__(self):
        # Close the session
        session.close()


