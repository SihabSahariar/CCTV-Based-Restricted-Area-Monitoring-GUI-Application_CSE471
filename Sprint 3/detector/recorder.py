import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
# import tkinter as tk
# from tkinter import Button
import time

Gst.init(None)

class CameraRecorder:
    def __init__(self, rtsp_uri, output_file):
        self.rtsp_uri = rtsp_uri
        self.output_file = output_file
        self.pipeline = None

    def start_recording(self):
        max_file_duration_ns = 86400000000000
        
        # self.pipeline = Gst.parse_launch(
        #     f'rtspsrc location={self.rtsp_uri} ! decodebin ! queue ! videoconvert ! x264enc ! mp4mux ! filesink location={self.output_file}'

        # )
        self.pipeline = Gst.parse_launch(
                f"rtspsrc location={self.rtsp_uri} latency=500 ! "
                f"rtph264depay ! h264parse ! "
                f"matroskamux ! multifilesink location={self.output_file} "
                f"next-file=max-duration max-file-duration={max_file_duration_ns}")

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_bus_message)

        self.pipeline.set_state(Gst.State.PLAYING)

    def stop_recording(self):
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)

    def on_bus_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"Error: {err}, Debug: {debug}")
        elif t == Gst.MessageType.EOS:
            print("End of Stream")
            self.stop_recording()

'''
rtsp_url = "rtsp://admin:admin123@192.168.0.21:554:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif"
output_file = "output.mp4"
recorder = CameraRecorder(rtsp_url, output_file)
recorder.start_recording()
time.sleep(10)
recorder.stop_recording()
'''

# class CameraRecorderApp(tk.Tk):
#     def __init__(self):
#         super(CameraRecorderApp, self).__init__()
#         self.rtsp_uri = "rtsp://admin:admin123@192.168.0.21:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif"
#         self.output_file = "output.mp4"

#         self.recorder = CameraRecorder(self.rtsp_uri, self.output_file)

#         self.start_button = Button(self, text="Start Recording", command=self.on_start_clicked)
#         self.start_button.pack(side=tk.LEFT)

#         self.stop_button = Button(self, text="Stop Recording", command=self.on_stop_clicked)
#         self.stop_button.pack(side=tk.LEFT)

#     def on_start_clicked(self):
#         self.recorder.start_recording()

#     def on_stop_clicked(self):
#         self.recorder.stop_recording()

# if __name__ == "__main__":
#     app = CameraRecorderApp()
#     app.mainloop()
