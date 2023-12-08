from picamera2 import Picamera2, Preview
import subprocess
import time

picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
picam2.start_preview(Preview.QTGL)
picam2.start()
while True:
    continue
picam2.start_and_record_video("test.mp4", duration=15)

#time.sleep(15)
cmd = ['ffmpeg', '-i', 'test.mp4', '-vf', 'transpose=2,transpose=2', 'test.mp4']
