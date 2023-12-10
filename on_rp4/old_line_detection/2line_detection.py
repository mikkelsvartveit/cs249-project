from picamera2 import Picamera2
import cv2
import numpy as np
from steering import Steer


# Camera calibration parameters
camera_matrix = np.array([[317.30214047, 0, 271.11362538],
                          [0, 318.10923877, 220.40418086],
                          [0, 0, 1]])

dist_coeffs = np.array([-0.31776678, 0.12431899, 0, 0, -0.0258798060])

def undistort(frame):
    h, w = frame.shape[:2]
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))
    undistorted = cv2.undistort(frame, camera_matrix, dist_coeffs, None, new_camera_matrix)
    x, y, w, h = roi
    undistorted = undistorted[y:y+h, x:x+w]
    return undistorted

def find_line(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Thresholding
    _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Filter out contours that are too large (like the edges of the frame)
        contours = [c for c in contours if cv2.contourArea(c) < frame.shape[0] * frame.shape[1] * 0.9]

        if contours:  # Check again if there are any contours left
            largest_contour = max(contours, key=cv2.contourArea)
            return largest_contour
    return None

def control_robot(line, frame):
    steer = Steer()
    M = cv2.moments(line)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    else:
        cX, cY = 0, 0

    frame_width = frame.shape[1]
    center_x_frame = frame_width // 2

    if cX < center_x_frame - 10:
        # TODO: Implement robot's left steering command
        print('left')
        steer.turn_left()
        pass
    elif cX > center_x_frame + 10:
        # TODO: Implement robot's right steering command
        print('right')
        steer.turn_right()
        pass
    else:
        # TODO: Implement robot's forward command
        print('forward')
        steer.forward()
        pass

def main():
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration()
    picam2.configure(camera_config)
    picam2.start()

    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        #frame = undistort(frame)


        # Crop to the bottom half of the frame
        #height = frame.shape[0]
        #frame = frame[height//2:, :]

        line = find_line(frame)

        if line is not None:
            control_robot(line, frame)
            cv2.drawContours(frame, [line], -1, (0, 255, 0), 3)

        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    picam2.stop()

if __name__ == '__main__':
    main()
