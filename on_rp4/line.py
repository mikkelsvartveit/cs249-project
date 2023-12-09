#!/usr/bin/env python3
# Updated OpenCV Line Detection Script
import math
import cv2
import numpy as np

def calculate_slope(x1, x2, y1, y2):
    """
    Calculate the slope of a line given two points.
    
    Args:
        x1 (int): X-coordinate of the first point
        x2 (int): X-coordinate of the second point
        y1 (int): Y-coordinate of the first point
        y2 (int): Y-coordinate of the second point

    Returns:
        float: The slope of the line in degrees
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
        frame (numpy.ndarray): The current video frame

    Returns:
        numpy.ndarray: The thresholded frame
    """
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    equalized_frame = cv2.equalizeHist(gray_frame)
    blurred_frame = cv2.GaussianBlur(equalized_frame, (5, 5), 0)
    _, thresholded_frame = cv2.threshold(blurred_frame, 240, 255, cv2.THRESH_BINARY)
    return thresholded_frame

def main():
    video_capture = cv2.VideoCapture(0)

    is_left_turn = False
    is_right_turn = False
    is_straight = False

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        frame = cv2.resize(frame, (600, 600))
        thresholded_frame = process_frame(frame)

        # Find contours
        contours, _ = cv2.findContours(thresholded_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw contours
        cv2.drawContours(thresholded_frame, contours, -1, (255, 0, 0), 3)

        # Line detection
        lines = cv2.HoughLinesP(thresholded_frame, 1, np.pi / 180, 25, minLineLength=10, maxLineGap=40)

        left_count = right_count = 0
        for line in lines:
            for x1, y1, x2, y2 in line:
                line_angle = calculate_slope(x1, x2, y1, y2)
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

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()