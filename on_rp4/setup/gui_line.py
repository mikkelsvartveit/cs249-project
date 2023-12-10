import cv2
import numpy as np
from tkinter import *
from picamera2 import Picamera2
from threading import Thread
import math



def update_lower_threshold(val):
    global low_threshold
    low_threshold = int(val)

def update_upper_threshold(val):
    global high_threshold
    high_threshold = int(val)

def update_rho(val):
    global rho
    rho = val*np.pi/180

def update_theta(val):
    global theta
    theta = int(val)

def update_min_line_lenth(val):
    global min_line
    min_line = int(val)

def update_max_line_gap(val):
    global max_line_gap
    max_line_gap = int(val)
    


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

def process_image():
    global low_threshold, high_threshold, rho, theta, min_line, max_line_gap

    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (600, 600))
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)    
        
        # Use global threshold values
        canny_edges = cv2.Canny(blurred_frame, low_threshold, high_threshold)
        
        # Set the top half of the image to black
        height = canny_edges.shape[0]
        canny_edges[:height // 2, :] = 0
        cv2.imshow('canny edge', canny_edges)

        # Use global Hough transform parameters
        lines = cv2.HoughLinesP(canny_edges, rho, theta, 25, minLineLength=min_line, maxLineGap=max_line_gap)

        left_count = right_count = 0
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    line_angle = calculate_slope(x1, y1, x2, y2)
                    if 250 < y1 < 600 and 250 < y2 < 600:
                        if -80 <= line_angle <= -30:
                            right_count += 1
                            left_count = 0
                            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2, cv2.LINE_AA)
                        elif 30 <= line_angle <= 80:
                            left_count += 1
                            right_count = 0
                            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow('Processed Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Initialize camera
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
picam2.start()

# GUI
root = Tk()
root.title("Parameter Tuning")

# Initialize threshold value
#threshold_value = 200
low_threshold = 50
high_threshold = 150
rho = np.pi / 180
theta = 25
min_line = 10
max_line_gap = 40

# GUI
root = Tk()
root.title("Parameter Tuning")

# Slider for rho value
Label(root, text="Rho Value (pixels)").pack()  # Adjusted label for clarity
rho_slider = Scale(root, from_=1, to_=10, orient=HORIZONTAL, command=update_rho)
rho_slider.set(rho * 180 / np.pi)  # Convert initial rho value from radians to degrees for the slider
rho_slider.pack()

# Slider for theta value
Label(root, text="Theta Value (degrees)").pack()  # Adjusted label for clarity
theta_slider = Scale(root, from_=1, to_=180, orient=HORIZONTAL, command=update_theta)
theta_slider.set(theta * 180 / np.pi)  # Convert initial theta value from radians to degrees for the slider
theta_slider.pack()

# Slider for min line length value
Label(root, text="Min Line Length (pixels)").pack()
min_line_slider = Scale(root, from_=10, to_=200, orient=HORIZONTAL, command=update_min_line_lenth)
min_line_slider.set(min_line)
min_line_slider.pack()

# Slider for max line gap value
Label(root, text="Max Line Gap (pixels)").pack()
max_line_slider = Scale(root, from_=10, to_=200, orient=HORIZONTAL, command=update_max_line_gap)
max_line_slider.set(max_line_gap)
max_line_slider.pack()


# Start the image processing in a separate thread
Thread(target=process_image).start()

root.mainloop()
