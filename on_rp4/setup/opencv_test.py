from picamera2 import Picamera2
import cv2
import numpy as np

def main():
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration()
    picam2.configure(camera_config)
    picam2.start()

    while True:
        # Capture a frame
        frame = picam2.capture_array()

        # Convert to a format OpenCV can use
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

        # Display the frame using OpenCV
        cv2.imshow('Frame', frame)

        # Break the loop with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cv2.destroyAllWindows()
    picam2.stop()

if __name__ == '__main__':
    main()
