import cv2
import re
import argparse
import time
import os
import logging

from securitycamera.slack import Slack
from securitycamera.intruderdetector import IntruderDetector



def setupLogger():
    # create logger with 'spam_application'
    myLogger = logging.getLogger('security_camera')
    myLogger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('security_camera.log')
    fh.setLevel(logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    myLogger.addHandler(fh)
    myLogger.addHandler(ch)
    return myLogger


logger = setupLogger()
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", type=str, default ="/data/videos/incoming",
	help="path to optional input video directory")

ap.add_argument("-i", "--input", type=str,
	help="path to optional input video file")


ap.add_argument("-c","--clear-slack-files", action='store_true',
	help="clears files in slack")

ap.add_argument("-slack", "--slack-config-path", type=str, default="./config.ini",
	help="path to optional slack configuration")

ap.add_argument("-s", "--skip-frames", type=int, default=30,
	help="# of skip frames between detections")
args = vars(ap.parse_args())



def wait_for_video(directory, time_limit=3600, check_interval=60):
    '''Return next video file to process, if not keep checking once every check_interval seconds for time_limit seconds.
    time_limit defaults to 1 hour
    check_interval defaults to 1 minute
    '''

    now = time.time()
    last_time = now + time_limit

    while time.time() <= last_time:
        logger.info("Searching for new camera uploads")
        for root, dirs, files in os.walk(directory):
            files = [fi for fi in files if fi.endswith(".mp4") and not fi.startswith(".")]
            for file in files:
                filePath = os.path.join(root, file)

                if not os.path.isfile(filePath + '.processed') and \
                        os.path.getsize(filePath) > 0 and \
                        isValidVideoFile(filePath):
                    return filePath

        # Wait for check interval seconds, then check again.
        time.sleep(check_interval)

    return None


def isValidVideoFile(file):
    cap = cv2.VideoCapture(file)
    totalFrameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    return totalFrameCount > 0

def moveVideoToArchive(file):
    open(file + '.processed', 'w').close()

def wait_for_videos(videosFolder):
    intruderDetector = IntruderDetector(args.get("slack_config_path"))
    while True:

        file = wait_for_video(videosFolder, 3600 * 354, 1)

        if file is None:
            continue

        result = intruderDetector.processFile(file)

        if result:
            moveVideoToArchive(file)



logger.info("OpenCV version :  {0}".format(cv2.__version__))
# if a video path was not supplied, search for files in the given
# folder
if args.get("clear_slack_files",False):
    slack = Slack(args.get("slack_config_path"))
    slack.clearFiles()
elif not args.get("input", False):
    logger.info("[INFO] Checking for new incoming files")
    wait_for_videos(args.get("directory"))
else:
    file =  args["input"]
    intruderDetector = IntruderDetector(args.get("slack_config_path"),debug=True)
    intruderDetector.processFile(file)