from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, Interval, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
import warnings
from sqlalchemy import exc as sa_exc
# Ignore INFO level messages from SQLAlchemy
warnings.filterwarnings("ignore", category=sa_exc.SAWarning)
# Create an engine for the database
engine = create_engine('sqlite:///database.db')
# engine = create_engine('mysql+pymysql://username:password@host/database_name')
# engine = create_engine('postgresql://username:password@host/database_name')

# Create a base class for declarative models
Base = declarative_base()

# Define the Camera table
class Camera(Base):
    __tablename__ = 'camera'
    camera_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    camera_name = Column(Text, nullable=False)
    ip_address = Column(Text, nullable=False)
    username = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    sample_image_path = Column(Text, nullable=False)
    numbers_of_slot = Column(Integer, nullable=False)  
    created_at = Column(DateTime, nullable=False)  
    updated_at = Column(DateTime, nullable=False)
    location = Column(Text, nullable=False)
    slots = relationship("Slot", backref="camera")

# Define the Coordinates table
class Coordinates(Base):
    __tablename__ = 'coordinates'
    coordinates_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    # slot_id = Column(Integer, ForeignKey('slot.slot_id'), nullable=False)
    x1 = Column(Integer, nullable=False)
    y1 = Column(Integer, nullable=False)
    x2 = Column(Integer, nullable=False)
    y2 = Column(Integer, nullable=False)
    slot = relationship("Slot", uselist = False, backref="coordinates")

# Define the Slot table
class Slot(Base):
    __tablename__ = 'slot'
    slot_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    camera_id = Column(Integer, ForeignKey('camera.camera_id'), nullable=False)
    coordinates_id = Column(Integer, ForeignKey('coordinates.coordinates_id'), nullable=False)
    slot_number = Column(Integer, nullable=False)
    occupancy_status = Column(Boolean)
    reference_images = relationship("ReferenceImage", backref="slot")
    occupancy_history = relationship("OccupancyHistory", backref="slot")


# Define the ReferenceImage table
class ReferenceImage(Base):
    __tablename__ = 'reference_image'
    reference_image_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    slot_id = Column(Integer, ForeignKey('slot.slot_id'), nullable=False)
    image_path = Column(Text)
    last_updated = Column(DateTime)
    ref_img_occupancy = Column(Boolean)

# Define the RecordedVideo table
class RecordedVideo(Base):
    __tablename__ = 'recorded_video'
    recorded_video_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    exit_video_path = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    occupancy_history = relationship("OccupancyHistory", backref="recorded_video")

# Define the OccupancyHistory table
class OccupancyHistory(Base):
    __tablename__ = 'occupancy_history'
    occupancy_history_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    slot_id = Column(Integer, ForeignKey('slot.slot_id'), nullable=False)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime)
    duration = Column(Text)
    recorded_video_id = Column(Integer, ForeignKey('recorded_video.recorded_video_id'), nullable=True)


    

# Create the tables in the database
Base.metadata.create_all(engine)

# # Create a session factory
Session = sessionmaker(bind=engine)

# # Create a session object
session = Session()
