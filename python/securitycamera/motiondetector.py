import cv2
import imutils
import numpy as np
from imutils.object_detection import non_max_suppression
class MotionDetector(object):


    def __init__(self):
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=40)
        self.minDetectArea = 200

    def applyBackgroundSubtraction(self, resizedFrameGray):
        backgroundSubtractionFrame = self.fgbg.apply(resizedFrameGray)
        backgroundSubtractionFrame = self.removeWhiteNoise(backgroundSubtractionFrame)
        backgroundSubtractionFrame = cv2.dilate(backgroundSubtractionFrame, None, iterations=2)
        return backgroundSubtractionFrame


    def removeWhiteNoise(self, frame):
        # find contours in the image and initialize the mask that will be
        # used to remove the bad contours
        (_,cnts,_)= cv2.findContours(frame.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.ones(frame.shape[:2], dtype="uint8") * 255

        # loop over the contours
        for c in cnts:
            # if the contour is bad, draw it on the mask
            if cv2.contourArea(c) < self.minDetectArea:
                cv2.drawContours(mask, [c], -1, 0, -1)

        # remove the contours from the image and show the resulting images
        frame = cv2.bitwise_and(frame, frame, mask=mask)
        return frame

    def detectObjectsByMotion(self, frameColor, resizedFrameGray):
        backgroundSubtractionFrame = self.applyBackgroundSubtraction(frameColor)

        cnts = cv2.findContours(backgroundSubtractionFrame.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        boxes = []
        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < self.minDetectArea:
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            boxes.append((x, y, x+w, y+h))

        return (backgroundSubtractionFrame,boxes)