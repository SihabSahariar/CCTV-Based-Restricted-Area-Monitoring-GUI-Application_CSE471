import threading
import cv2
import os
import configparser
import redis
import json

config = configparser.ConfigParser()
config.read('config.ini')
enable_redis = config.getboolean('I/O', 'enable_redis')

redis_host_new = config['I/O']['redis_server'] 
redis_host = redis_host_new.split(":")[0]
redis_port = int(redis_host_new.split(":")[1])


if enable_redis:
	client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

class RecordingThread:
    def __init__(self, output_file, recorded_frames):
        self.output_file = output_file
        self.recorded_frames = recorded_frames.copy()
        print(len(self.recorded_frames), self.output_file)
        self.thread = threading.Thread(target=self.run)

    def start(self):
        self.thread.start()

    def run(self):
        if self.output_file and self.recorded_frames:
            frame_height, frame_width, _ = self.recorded_frames[0].shape
            fps = 30
            fourcc = cv2.VideoWriter_fourcc(*'vp80')
            out = cv2.VideoWriter(self.output_file, fourcc, fps, (frame_width, frame_height))
            print(len(self.recorded_frames))
            for frame in self.recorded_frames:
                out.write(frame)
            out.release()
            try:
                file_size = os.path.getsize(self.output_file)/1024

                if file_size>100:
                    print('Send signal to redis')
                    self.send_message()
            except Exception as e:
                print(f"Recording Error {e} : recorder.py-> Line 44")

    def send_message(self):
        channel = "lynkeus_parking_recorded"
        message = {'recorded':"true"}
        message = json.dumps(message)
        client.publish(channel, message)
