from sqlalchemy.orm import sessionmaker
import os
import sys
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
os.environ['SQLALCHEMY_ENGINE_LOGGING'] = 'False'
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
from database_setup import *
database_file = 'database.db'
engine = create_engine(f'sqlite:///{database_file}', echo=True)

# Create a session factory
Session = sessionmaker(bind=engine)

def get_slot_id(camera_id, slot_number):
    # Create a session object
    session = Session()
    slot_id = (
        session.query(Slot.slot_id)
                .join(Camera)
                .filter(Camera.camera_id == camera_id)
                .filter(Slot.slot_number == slot_number)
                .first()
        )
    session.close()
    if slot_id:
        return slot_id[0]
    else:
        return None
    

def get_reference_image_id(camera_id, slot_number):
    # Create a session object
    session = Session()
    reference_image_id = (
         session.query(ReferenceImage.reference_image_id)
                .join(Slot)
                .join(Camera)
                .filter(Camera.camera_id == camera_id)
                .filter(Slot.slot_number == slot_number)
                # .filter(ReferenceImage.hour == hour)
                .first()
    )
    session.close()
    if reference_image_id:
        return reference_image_id[0]
    else:
        return None

def get_occupancy(camera_id):  # Slot Occupancy From Database Slot
    # Create a session object
    # session = Session()
    # ref_occupancies = (
	# 	session.query(ReferenceImage.ref_img_occupancy)
    #             .join(Slot)
    #             .join(Camera)
    #             .filter(Camera.camera_id == camera_id)
    #             # .filter(ReferenceImage.hour == -1)
    #             .all()
	# )
    # ref_occupancies = [occupancy[0] for occupancy in ref_occupancies]
    # session.close()
    # print(f"Camera ID: {camera_id} Occupancy: {ref_occupancies}")
    session = Session()

    try:
        slots_occupancy = (
            session.query(Slot.occupancy_status)
            .join(Camera)
            .filter(Camera.camera_id == camera_id)
            .all()
        )

        occupancy_list = [occupancy[0] for occupancy in slots_occupancy]
        return occupancy_list
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

    # return ref_occupancies
    
    
def get_slots_entry_time(camera_id):
    # Create a session object
    session = Session()
    # Query the entry_time values
    entry_times = (
        session.query(OccupancyHistory.entry_time)
                .join(OccupancyHistory.slot)
                .join(Slot.camera)
                .filter(Camera.camera_id == camera_id)
                .all()
    )

    # Store the entry_time values in a list
    entry_time_list = [entry_time[0] for entry_time in entry_times]
    session.close()
    return entry_time_list
    
    


def get_positions(camera_id):
    # print("From Camera Occupancy#############################################")
    camera_id = int(camera_id)
    session = Session()

    occu = []
    posList = []
    

    # Retrieve the camera with the given camera_id
    camera = (
        session.query(Camera)
        .filter(Camera.camera_id == camera_id)
        .first()
    )

    # Check if the camera exists
    if camera:
        # Retrieve the slots associated with the camera
        slots = (
            session.query(Slot)
                    .filter(Slot.camera_id == camera.camera_id)
                    .order_by(Slot.slot_id).all()
        )

        # Check if the slots exist
        if slots:
            # Iterate over the slots
            for slot in slots:
                # Retrieve the coordinates for each slot
                coordinates = slot.coordinates

                # Now you can access the coordinates of the slot
                posList.append((coordinates.x1, coordinates.y1, coordinates.x2, coordinates.y2))
        else:
            print("Slots not found for the camera.")
    else:
        print("Camera not found.")

    # Close the session
    session.close()

    return posList


if __name__ == '__main__':
    # Example usage: Retrieve occupancy and positions for camera_id = 1
    camera_id = 1
    slot_number = 1
    occupancy = get_occupancy(camera_id)
    positions = get_positions(camera_id)
    slot_id = get_slot_id(camera_id, slot_number)
    ref_id = get_reference_image_id(camera_id, slot_number)
    # print(ref_id)
    # print("Positions:")
    # print(positions)
