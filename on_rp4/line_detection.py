import cv2
import numpy as np
from picamera2 import Picamera2
import utils
from steering import Steer
rou = 0
curve_list = []
avgVal1 = 10

def getLaneCure(img, display=2):
    imgCopy = img.copy()
    imgResult = img.copy()
    # Step 1: Thresholding
    imgThres = utils.thresholding(img)

    # Step 2: Warp image
    h, w, c = img.shape
    points = utils.valTrackbars()
    imgWarp = utils.warpImg(imgThres, points, w, h)
    imgWarpPoints = utils.drawPoints(imgCopy, points)

    # Step 3: Histogram
    middel_point, imgHist = utils.getHistogram(imgWarp, display=True, minPer=0.4, region=4)
    curve_average, imgHist = utils.getHistogram(imgWarp, display=True, minPer=0.6, region=1)
    curve_raw = curve_average - middel_point

    # Step 4: Get steering angle
    curve_list.append(curve_raw)
    # maintain fixed number of elements in list
    if len(curve_list) > avgVal1:
        curve_list.pop(0)
    curve = int(sum(curve_list) / len(curve_list))

    # Step 5: Display
    if display != 0:
        imgInvWarp = utils.warpImg(imgWarp, points, w, h, inv=True)
        imgInvWarp = cv2.cvtColor(imgInvWarp, cv2.COLOR_GRAY2BGR)
        imgInvWarp[0: h// 3, 0: w] = 0, 0, 0
        imgLaneColor = np.zeros_like(img)
        imgLaneColor[:] = 0, 255, 0
        imgLaneColor = cv2.bitwise_and(imgInvWarp, imgLaneColor)
        imgResult = cv2.addWeighted(imgResult, 1, imgLaneColor, 1, 0)
        midY = 450
        cv2.putText(imgResult, str(curve), (w//2-80, 85), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 3)
        cv2.line(imgResult, (w//2, midY), (w//2 + (curve*3), midY), (255, 0, 255), 5)
        cv2.line(imgResult, ((w//2 + (curve*3)), midY - 25), (w//2 + (curve*3), midY + 25), (0, 255, 0), 5)
        for x in range(-30, 30):
            w1 = w//20
            cv2.line(imgResult, (w1*x + int(curve//50), midY - 10),
                     (w1*x + int(curve//50), midY + 10), (0, 0, 255), 2)
        #fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
        #cv2.putText(imgResult, 'FPS {}'.format(int(fps)), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        if display == 2:
            imgStacked = utils.stackImages(0.7, ([img, imgWarpPoints, imgWarp],
                                                 [imgHist, imgLaneColor, imgResult]))
            cv2.imshow('ImageStack', imgStacked)
        elif display == 1:
            cv2.imshow('Resutlt', imgResult)
    
    # Step 6: Return curve value
    curve = curve / 100
    if curve > 1: curve == 1
    if curve < -1: curve == -1
    return curve

if __name__ == '__main__':
    steer = Steer()
    #steer.keyboard()
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration()
    picam2.configure(camera_config)
    picam2.start()
    initialTrackbarVals = [93, 155, 0, 211]
    utils.InitializeTrackbars(initialTrackbarVals)
    while True:
        #success, img = cap.read()
        img = picam2.capture_array()
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img = cv2.resize(np.array(img), (480, 240))
        curve = getLaneCure(img, display=2)
        print("kjør")
        if curve < -0.3:
            #pass
            steer.turn_left()
        elif curve > 0.3:
            #pass
            steer.turn_right()
        else:
            #pass
            steer.forward()
        print(curve)
    
        # TODO: implement keyboard override
        cv2.waitKey(1)
