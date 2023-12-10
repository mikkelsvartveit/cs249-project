from picamera2 import Picamera2
import cv2
import numpy as np
from steering import Steer
from collections import deque


decision_history = deque(maxlen=5)  # Adjust '5' based on desired smoothing


def find_line(frame):
    # Convert to HSV for better color filtering
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define range for white color
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 25, 255])

    # Threshold the HSV image to get only white colors
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)

    # Use Canny Edge Detection
    edges = cv2.Canny(blurred, 50, 150)

    # Debugging: Display the mask and edges
    cv2.imshow('Mask', mask)
    cv2.imshow('Edges', edges)

    # Use Hough Line Transform to find lines
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=20, minLineLength=50, maxLineGap=30)

    if lines is not None:
        print(f"Found {len(lines)} lines")
        # Draw all detected lines for debugging
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)

        # Process lines in the lower half of the image
        frame_center = frame.shape[1] // 2
        bottom_half_lines = [line for line in lines if line[0][1] > frame.shape[0] / 2 or line[0][3] > frame.shape[0] / 2]

        # Determine the predominant side of the lines in the lower half
        left_lines = [line for line in bottom_half_lines if max(line[0][0], line[0][2]) < frame_center]
        right_lines = [line for line in bottom_half_lines if min(line[0][0], line[0][2]) > frame_center]

        return left_lines, right_lines

    print("No lines found")
    return [], []

def control_robot(lines, frame):
    steer = Steer()

    # Determine the average position of all lines
    if lines:
        avg_x = np.mean([line[0][0] + line[0][2] for line in lines]) / 2
    else:
        avg_x = frame.shape[1] / 2  # Default to the center

    # Decide direction based on the average position
    frame_center = frame.shape[1] / 2
    if avg_x < frame_center:  # More lines on the left, robot should turn right
        decision = "right"
    elif avg_x > frame_center:  # More lines on the right, robot should turn left
        decision = "left"
    else:
        decision = "forward"

    # Add the current decision to the history
    decision_history.append(decision)

    # Determine the most frequent decision in the history
    most_common_decision = max(set(decision_history), key=decision_history.count)

    # Execute the most common decision (inverted logic)
    if most_common_decision == "left":
        print("Turning Right")
        # steer.turn_right()
    elif most_common_decision == "right":
        print("Turning Left")
        # steer.turn_left()
    else:
        print("Going Straight")
        # steer.forward()

def main():
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration()
    picam2.configure(camera_config)
    picam2.start()

    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

        left_lines, right_lines = find_line(frame)
        all_lines = left_lines + right_lines  # Combine left and right lines into a single list
        if all_lines:
            control_robot(all_lines, frame)  # Pass the combined list to control_robot

        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    picam2.stop()

if __name__ == '__main__':
    main()


