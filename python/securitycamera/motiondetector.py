import cv2
import imutils
import numpy as np
import itertools
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

    def merge(self, box1, box2):
        (b1startx, b1starty, b1endx, b1endy) = box1
        (b2startx, b2starty, b2endx, b2endy) = box2
        mergedStartx = min(b1startx, b2startx)
        mergedStarty = min(b1starty, b2starty)
        mergedEndy = max(b1endy, b2endy)
        mergedEndx = max(b1endx, b2endx)

        return (mergedStartx, mergedStarty, mergedEndx, mergedEndy)

    def stacked(self, box1, box2):
        (b1startx, b1starty, b1endx, b1endy) = box1
        (b2startx, b2starty, b2endx, b2endy) = box2

        maxDiff = 50

        diffstartx = abs(b1startx - b2startx)
        diffendx = abs(b1endx - b2endx)

        # the two boxes should be in almost the same col
        # but not necessarily exactly the same within a tolerance
        # maxDiff

        isStackedX = diffstartx <= maxDiff and diffendx <= maxDiff

        #for the y axis the same applies to the bottomm of the rectangle
        # we ignore the starting point of the box which is stacked on top
        minendY = min(b1endy,b2endy)
        maxstartY = max(b1endy,b2endy)
        diffY = abs(maxstartY - minendY)

        isStackedY = diffY <=maxDiff
        print("box1 {} box2 {} isStackedX {} isStackedY {}".format(box1,box2,isStackedX,isStackedY))
        return isStackedX and isStackedY



    def mergeCloseBoundingBoxes(self, boxes):
        deleteBoxes = []
        mergedBoundingBoxes = []

        for (box1,box2) in itertools.combinations(boxes, 2):
            if self.stacked(box1, box2):
                mergedBox = self.merge(box1, box2)
                mergedBoundingBoxes.append(mergedBox)
                deleteBoxes.append(box1)
                deleteBoxes.append(box2)

        merged = boxes + mergedBoundingBoxes
        for item in deleteBoxes:
            merged.remove(item)

        print("returning merged bounding boxes {}".format(merged))
        return merged


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
        if len(boxes)>1:
            boxes = self.mergeCloseBoundingBoxes(boxes)
        return (backgroundSubtractionFrame,boxes)