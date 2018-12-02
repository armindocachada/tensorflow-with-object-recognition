import numpy as np
import cv2
from collections import OrderedDict
from scipy.spatial import distance as dist

class TrackedObject(object):
    def __init__(self, objectID, frameNumber, centroid):
        self.objectID = objectID
        self.centroids =[]
        self.disappeared = 0
        self.centroids.append((frameNumber,centroid))
    def centroid(self):
        (_, centroid) = self.centroids[-1]
        return centroid

    def addCentroid(self, frameNumber, newCentroid):
        self.centroids.append((frameNumber, newCentroid))

    def updatePositionWithEstimate(self, frameNumber):
        (lastFrameNumber, lastCentroid) = self.centroids[-1]
        (speedx, speedy) = self.calculateCentroidSpeedPerFrame()
        numberOfFrames = frameNumber - lastFrameNumber
        (cx, cy) = lastCentroid
        estimatedCentroid = (cx + int(speedx * numberOfFrames), cy + int(speedy * numberOfFrames) )
        self.addCentroid(frameNumber, estimatedCentroid)


    def calculateCentroidSpeedPerFrame(self):
        if len(self.centroids) <= 1:
            return (0,0)
        else:
            (lastFrameNumber, (lcx, lcy)) = self.centroids[-1]
            (previousFrameNumber, (pcx, pcy)) = self.centroids[-2]

            speedx = float((lcx-pcx) / (lastFrameNumber - previousFrameNumber))
            speedy = float((lcy-pcy) / (lastFrameNumber - previousFrameNumber))
            return (speedx, speedy)


class Tracker(object):

    def __init__(self, maxDistance=100, maxDisappeared=10):
       self.objects = OrderedDict()
       self.maxDistance = maxDistance
       self.maxDisappeared = maxDisappeared
       self.nextObjectID=0

    def allocateObjectID(self):
        allocatedbjectID = self.nextObjectID
        self.nextObjectID = self.nextObjectID + 1
        return allocatedbjectID

    def register(self, frameNumber, centroid):
        objectID = self.allocateObjectID()
        object = TrackedObject(objectID, frameNumber, centroid)
        self.objects[objectID]=object

    def updateTrackers(self, frameNumber, image, boundingBoxes,showTrackers=False):
        # for each bounding box calculate centroid
        newCentroids = []
        for box in boundingBoxes:
            (startX, startY, endX, endY) = box
            centroidX = int((startX + endX) / 2.0)
            centroidY = int((startY + endY) / 2.0)
            centroid = (centroidX, centroidY)
            newCentroids.append(centroid)
        # if there are no trackers created
        # we initialise them
        if not self.objects:
            for i,centroid in enumerate(newCentroids):
                newObject = TrackedObject(i, frameNumber, centroid)
                self.objects[i] = newObject
        else:
            # new centroids have been calculated
            # we have now to pair them with the correct trackers
            self.pairCentroidsWithObjects(frameNumber, newCentroids)

        if showTrackers:
            for obj in self.objects.values():
                text = "ID {}".format(obj.objectID)
                centroid = obj.centroid()
                cv2.putText(image, text, (centroid[0] - 10, centroid[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.circle(image, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)


    def updateDisappearedObjects(self, frameNumber, objectsDisappeared):
        toDelete = []
        for objectDisappeared in objectsDisappeared:
            objectDisappeared.disappeared= objectDisappeared.disappeared+1
            # update the disappeared object with an estimate
            # in case we know the direction where it was heading
            objectDisappeared.updatePositionWithEstimate(frameNumber)
            if (objectDisappeared.disappeared> self.maxDisappeared):
                toDelete.append(objectDisappeared)
        for itemToDelete in toDelete:
            del self.objects[itemToDelete.objectID]


    def calculateAffinityWithOldObjects(self,newCentroids,oldObjects):
        if not newCentroids:
            return None

        oldCentroids = [oldObject.centroid() for oldObject in oldObjects.values()]

        return dist.cdist(np.array(oldCentroids), newCentroids)

    def pairCentroidsWithObjects(self,frameNumber, newCentroids):

        if not newCentroids:
            self.updateDisappearedObjects(frameNumber, self.objects.values())
            return
        # compute the distance between each pair of object
        # centroids and input centroids, respectively -- our
        # goal will be to match an input centroid to an existing
        # object centroid
        D = self.calculateAffinityWithOldObjects(newCentroids, self.objects)
        # in order to perform this matching we must (1) find the
        # smallest value in each row and then (2) sort the row
        # indexes based on their minimum values so that the row
        # with the smallest value as at the *front* of the index
        # list
        rows = D.min(axis=1).argsort()

        # next, we perform a similar process on the columns by
        # finding the smallest value in each column and then
        # sorting using the previously computed row index list
        cols = D.argmin(axis=1)[rows]

        # in order to determine if we need to update, register,
        # or deregister an object we need to keep track of which
        # of the rows and column indexes we have already examined
        usedRows = set()
        usedCols = set()
        toDelete = []
        # loop over the combination of the (row, column) index
			# tuples
        for (row, col) in zip(rows, cols):
            # if we have already examined either the row or
            # column value before, ignore it
            if row in usedRows or col in usedCols:
                continue

            # if the distance between centroids is greater than
            # the maximum distance, do not associate the two
            # centroids to the same object
            if D[row, col] > self.maxDistance:
                continue

            # otherwise, grab the object ID for the current row,
            # set its new centroid, and reset the disappeared
            # counter
            objectsList =  list(self.objects.values())
            obj=objectsList[row]
            obj.addCentroid(frameNumber, newCentroids[col])
            obj.disappeared = 0

            # indicate that we have examined each of the row and
            # column indexes, respectively
            usedRows.add(row)
            usedCols.add(col)

        # compute both the row and column index we have NOT yet
        # examined
        unusedRows = set(range(0, D.shape[0])).difference(usedRows)
        unusedCols = set(range(0, D.shape[1])).difference(usedCols)

        # in the event that the number of object centroids is
        # equal or greater than the number of input centroids
        # we need to check and see if some of these objects have
        # potentially disappeared
        if D.shape[0] >= D.shape[1]:
            # loop over the unused row indexes
            for row in unusedRows:
                # grab the object ID for the corresponding row
                # index and increment the disappeared counter
                objectID = list(self.objects.values())[row].objectID
                self.objects[objectID].disappeared+= 1

                # check to see if the number of consecutive
                # frames the object has been marked "disappeared"
                # for warrants deregistering the object
                if self.objects[objectID].disappeared > self.maxDisappeared:
                    toDelete.append(objectID)


        for delObjectId in toDelete:
            self.objects.pop(delObjectId,None)


        # otherwise, if the number of input centroids is greater
        # than the number of existing object centroids we need to
        # register each new input centroid as a trackable object

        for col in unusedCols:
            self.register(frameNumber, newCentroids[col])

