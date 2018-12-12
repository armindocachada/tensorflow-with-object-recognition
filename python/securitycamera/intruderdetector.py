from securitycamera.videoutils import VideoUtils


import cv2
import logging
import imutils
import os
from securitycamera.firebase import Firebase
from securitycamera.motiondetector import MotionDetector
from securitycamera.tensorflowdetector import TensorflowDetector
from securitycamera.tracking import Tracker
from securitycamera.slack import Slack

logger = logging.getLogger('security_camera')
class IntruderDetector(object):


    def __init__(self, slackConfigPath, firebaseCredentialsPath, debug=False):
        self.motionDetector = MotionDetector()
        self.detector = TensorflowDetector()
        self.debug = debug

        logger.info("Slack config path: {}".format(slackConfigPath))
        self.slack = Slack(slackConfigPath)

        logger.info("Firebase credentials  path: {}".format(firebaseCredentialsPath))

        if (firebaseCredentialsPath and os.path.isfile(firebaseCredentialsPath)):
            # setting up firebase admin config to push training files
            logger.info("Setting up firebase admin config to push detection images with %s" % firebaseCredentialsPath)
            self.firebase = Firebase(firebaseCredentialsPath)
        else:
            logger.info("No firebase credentatials file provided. No images will be uploaded to the cloud.")

    # blocks until it finds the next video to analyse


    def drawBoundingBoxes(self, frameColor, boundingBoxes, boxColor):
        for (xmin, ymin, xmax, ymax ) in boundingBoxes:
            cv2.rectangle(frameColor, (int(xmin), int(ymin)), (int(xmax), int(ymax)), boxColor, 2)

            #cv2.rectangle(frameColor, (x, y), (x + w, y + h), (0, 255, 0), 2)
           # print("Bounding box: {}".format((x, y, x + w, y + h)))

    def filterOverlappingBoundingBoxes(self, bb, boundingBoxes):
        return [elem for elem in boundingBoxes if not VideoUtils.overlap(bb, elem)]

    def isInRestrictedArea(self,frame):
        (H, W) = frame.shape[:2]
        if self.tracker.objects:
            for obj in self.tracker.objects.values():
                if obj.disappeared == 0 and len(obj.centroids) > 1:
                    (cx, cy) = obj.centroid()
                    limitY = cx * (-1 * H / (3 * W)) + H
                    if cy > limitY:
                        logger.info("Object id {} in restricted area! Limit y {} and coordinates {}".format(
                            obj.objectID, limitY, (cx, cy)))
                        # here we can send a slack notification and break the while loop
                        return True
        return False

    def preprocess(self, frame):
        # resize
        resizedFrame = imutils.resize(frame, width=500)

       # (height, width) = resizedFrame.shape[:2]
       # padding = 300 - height
       # BLACK = [0, 0, 0]
       # padded = cv2.copyMakeBorder(resizedFrame, padding, 0, 0, 0, cv2.BORDER_CONSTANT, value=BLACK)

        # switch the frame to grayscale
        gray = cv2.cvtColor(resizedFrame, cv2.COLOR_BGR2GRAY)
        #apply gaussian blur
        #gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return (frame, resizedFrame, gray)

    def generateImageName(self, filePath, frameNumber):
        imageName = "{}.{}.png".format(os.path.basename(filePath), frameNumber)
        return imageName

    def processFile(self, file):
        # start the frames per second throughput estimator
        # fps = FPS().start()
        sunset = VideoUtils.isAfterSunset(file)
        self.tracker = Tracker()

        logger.info("processFile sunset=%s" %sunset)
        if sunset:
            logger.info("File %s was recorded after sunset." % file)
        else:
            logger.info("File %s was recorded in daytime." % file)

        cap = cv2.VideoCapture(file)

        totalFrameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        logger.info("Total frame count %d" % totalFrameCount)
        while True:
            currentFrame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            ret = cap.grab()
            logger.debug("Processing frame number {} out of {} frames".format(currentFrame, totalFrameCount))
            # update our frame counter

            if (not ret):
                logger.debug("Attempting to stop stream")
                cap.release()
                logger.info("Reached end of video file")
                break

            if currentFrame % 20 == 0:
                _, frame = cap.retrieve()

                (_, resizedFrameColor, resizedFrameGray) = self.preprocess(frame)
                (H, W) = resizedFrameColor.shape[:2]

                # lose all existing trackers
                #multiTracker = dict()
                (bsFrame,boundingBoxesMotion) = self.motionDetector.detectObjectsByMotion(resizedFrameColor, resizedFrameGray)
                self.tracker.updateTrackers(currentFrame, resizedFrameColor,boundingBoxesMotion, self.debug)

                if boundingBoxesMotion:
                    logger.debug("bounding boxes for motion detector {}".format(boundingBoxesMotion))
                    # self.drawBoundingBoxes(resizedFrameColor, boundingBoxesMotion, (0, 255, 0))
                if self.isInRestrictedArea(resizedFrameColor):
                    (_, _, boundingBoxesDetector) = self.detector.detectPerson(resizedFrameColor)
                    if boundingBoxesDetector:
                        logger.debug("bounding boxes for motion detector {}".format(boundingBoxesMotion))
                    cv2.line(resizedFrameColor, (0, H), (W, int(H * 2 / 3)), (255, 0, 0), 5)
                    self.drawBoundingBoxes(resizedFrameColor, boundingBoxesMotion, (0, 255, 0))
                    self.drawBoundingBoxes(resizedFrameColor, boundingBoxesDetector, (255, 0, 0))

                    #self.slack.notifySlack(file, resizedFrameColor, bsFrame)
                    # for training of model
                    # we upload to firebase if feature enabled
                    if self.firebase:
                        self.firebase.uploadImageForTraining(self.generateImageName(file,currentFrame), frame, resizedFrameColor, boundingBoxesMotion)
                    break;
            # update frame count
            # fps.update()
            if self.debug:
                cv2.imshow('frame', resizedFrameColor)
            #cv2.imshow('frame', resizedFrameColor)
            #cv2.imshow('preprocessed frame', bsFrame,)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break



        cap.release()
        # fps.stop()
        #print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
        #print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        return True