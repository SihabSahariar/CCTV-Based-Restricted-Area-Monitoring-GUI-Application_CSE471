import numpy as np
import cv2
import redis
import time 

import configparser
config = configparser.ConfigParser()
config.read('config.ini')
redis_host_new = config['I/O']['redis_server'] 
redis_host = redis_host_new.split(":")[0]
redis_port = int(redis_host_new.split(":")[1])
client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

def add_image_to_redis_stream(camera_id, slot_number, sample_img):

    # Generate the stream name
    stream_name = f"Cam_{camera_id}_Slot_{slot_number}"

    # Generate a timestamp for the current time
    field_time = str(time.time())

    # Encode the sample_img as PNG and get the image data in bytes
    img_byte = cv2.imencode('.png', sample_img)[1].tobytes()

    # Add the timestamped image data to the Redis stream
    entry_id = client.xadd(stream_name, {field_time: img_byte})

    return entry_id


def get_image_from_redis_stream(camera_id, slot_number, stream_id):

    # Generate the stream name
    stream_name = f"Cam_{camera_id}_Slot_{slot_number}"

    # Get the message data from the Redis stream using the stream ID
    message_data = client.xrange(stream_name, stream_id, stream_id)[0][1]

    # Get the image data from the message data dictionary
    image_data = next(iter(message_data.values()))

    # Convert the image bytes back to a NumPy array
    img_array = np.frombuffer(image_data, dtype=np.uint8)

    # Decode the NumPy array to a cv2 array
    img_cv2 = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    return img_cv2



