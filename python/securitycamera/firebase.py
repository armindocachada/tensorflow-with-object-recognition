import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import matplotlib.pyplot as plt
import cv2
import json
import logging
import json

logger = logging.getLogger('security_camera')
class Firebase(object):


    def __init__(self, firebaseCredentialsPath):
        # to avoid having two separate configuration
        # files, I decided to add the default bucket
        # name to the json file
        with open(firebaseCredentialsPath) as f:
            firebaseCred = json.load(f)


        cred = credentials.Certificate(firebaseCredentialsPath)
        default_app = firebase_admin.initialize_app(cred, {
            'storageBucket': firebaseCred["storageBucket"]
        })
        self.folderName = "uncleansed"

    # the tool we are using expects bounding boxes as:
    # xmin, ymin, width, height
    def convertBoundingBox(self, image, resizedImage, boundingBox):
        (H1, W1) = image.shape[:2]
        (H2, W2) = resizedImage.shape[:2]

        scaleX = float(H1/H2)
        scaleY = float(W1/W2)

        xmin = int(boundingBox[0] * scaleX)
        ymin = int(boundingBox[1] * scaleY)
        xmax = int(boundingBox[2] * scaleX)
        ymax = int(boundingBox[3] * scaleY)

        width = xmax - xmin
        height = ymax - ymin

        convertedBoundingBox = {"class":"person", "x": xmin,"y": ymin,
                                "width":  width,
                                "height": height
                                }

        return convertedBoundingBox

    def uploadImageForTraining(self, imageName, image, resizedImage, boundingBoxes):

        bucket = storage.bucket()
        source_file_name = "/tmp/{}".format(imageName)
        destination_blob_name = "{}/{}".format(self.folderName, imageName)

        imageRgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.imsave(source_file_name, imageRgb)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        logger.info('File {} uploaded to {}.'.format(
            source_file_name,
            destination_blob_name))

        # create json with bounding boxes and classes default to person
        dataJson = {}
        # for now we default to person detection class
        dataJson[imageName] ={
            "person":
                [ self.convertBoundingBox(image,resizedImage, bb)  for bb in boundingBoxes]
        }
        boundingBoxesJsonPath = "/tmp/{}.json".format(imageName)
        with open(boundingBoxesJsonPath, 'w') as outfile:
            json.dump(dataJson, outfile)

        blob = bucket.blob("{}/{}.json".format(self.folderName, imageName))
        blob.upload_from_filename(boundingBoxesJsonPath)