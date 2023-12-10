from picamera2 import Picamera2, Preview
from time import sleep

camera = Picamera2()
camera_config = camera.create_preview_configuration()
camera.configure(camera_config)
camera.start_preview(Preview.QTGL)
camera.start()
for i in range(5):
    print(i)
    sleep(1)
for i in range(10):
    sleep(5)  # Wait for 5 seconds between captures
    print('Capturing image %s...' % i)
    camera.capture_file('calibration_images/image%s.jpg' % i)
#camera.stop_preview()
