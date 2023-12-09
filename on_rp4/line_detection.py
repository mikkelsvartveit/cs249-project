#!/usr/bin/env python3
import math
import cv2
import numpy as np
from picamera2 import Picamera2

def calculate_slope(x1, y1, x2, y2):
    """
    Calculate the slope of a line given two points.
    
    Args:
        x1, y1: Coordinates of the first point.
        x2, y2: Coordinates of the second point.

    Returns:
        float: The slope of the line in degrees.
    """
    if x2 - x1 == 0:  # Prevent division by zero
        return float('inf')
    slope = float(y2 - y1) / float(x2 - x1)
    angle_radians = math.atan(slope)
    return angle_radians * (180 / np.pi)

def process_frame(frame):
    """
    Process the frame to prepare for line detection.
    
    Args:
        frame (numpy.ndarray): The current video frame.

    Returns:
        numpy.ndarray: The thresholded frame.
    """
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    equalized_frame = cv2.equalizeHist(gray_frame)
    blurred_frame = cv2.GaussianBlur(equalized_frame, (5, 5), 0)
    _, thresholded_frame = cv2.threshold(blurred_frame, 240, 255, cv2.THRESH_BINARY)
    return thresholded_frame

def main():
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration()
    picam2.configure(camera_config)
    picam2.start()

    is_left_turn = False
    is_right_turn = False
    is_straight = False

    while True:
        # Capture a frame using PiCamera2
        frame = picam2.capture_array()
        # Convert to a format OpenCV can use
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (600, 600))

        thresholded_frame = process_frame(frame)

        # Find contours
        contours, _ = cv2.findContours(thresholded_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw contours
        cv2.drawContours(thresholded_frame, contours, -1, (255, 0, 0), 3)

        # Line detection
        lines = cv2.HoughLinesP(thresholded_frame, 1, np.pi / 180, 25, minLineLength=10, maxLineGap=40)

        left_count = right_count = 0
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    line_angle = calculate_slope(x1, y1, x2, y2)
                    if 250 < y1 < 600 and 250 < y2 < 600:
                        if -80 <= line_angle <= -30:
                            right_count += 1
                            left_count = 0
                            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2, cv2.LINE_AA)
                        elif 30 <= line_angle <= 80:
                            left_count += 1
                            right_count = 0
                            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2, cv2.LINE_AA)

        # Determine direction
        if left_count >= 10 and not is_left_turn:
            print('left')
            is_left_turn = True
            is_right_turn = is_straight = False
        elif right_count >= 10 and not is_right_turn:
            print('right')
            is_right_turn = True
            is_left_turn = is_straight = False
        elif left_count < 10 and right_count < 10 and not is_straight:
            print('straight')
            is_straight = True
            is_left_turn = is_right_turn = False

        # Display the frames
        cv2.imshow('Thresholded Video', thresholded_frame)
        cv2.imshow('Processed Video', frame)

        # Break the loop with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cv2.destroyAllWindows()
    picam2.stop()

if __name__ == '__main__':
    main()
