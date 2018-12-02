import math
import cv2

class BrightestSpot(object):

    def __init__(self, radius):
        self.currentLocation = None
        self.moving = False
        self.radius = radius


    def updateLocation(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (self.radius, self.radius), 0)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
        #print("MinVal: %s MaxVal: %s MinLoc: %s MaxLox: %s" % (minVal, maxVal, minLoc, maxLoc))
        cv2.circle(image, maxLoc, self.radius, (255, 0, 0), 2)
        if not self.currentLocation is None:
            self.moving = self.currentLocation != maxLoc

        #print("Updating location to: %s and moving=%s. Previously location was %s" % (maxLoc, self.moving, self.currentLocation))

        self.currentLocation = maxLoc

    def isMoving(self):
        return self.moving

    def isIntersecting(self, boundingBox):
        circle = (self.currentLocation, self.radius)
        return self.intersect(circle, boundingBox)

    # determines if the given bounding box coordinates
    # intersect with the coordinates of our brightest spot
    @classmethod
    def intersect(cls, circle, rectangle):
        ((cx,cy), r) = circle
        (a, b, c, d) = rectangle


        return (cls.pointInRectangle((cx,cy), rectangle) or
                cls.intersectCircle(circle, (a, b)) or
                cls.intersectCircle(circle, (b, c)) or
                cls.intersectCircle(circle, (c, d)) or
                cls.intersectCircle(circle, (d, a)))




    @classmethod
    def distancePoints(cls, p1, p2):
        (x1, y1) = p1
        (x2, y2) = p2

        return math.hypot(x2 - x1, y2 - y1)

    @classmethod
    def intersectCircle(cls, circle, point):
        ((cx,cy),r) = circle
        (x,y) = point
        return cls.distancePoints((x, y), (cx,cy)) <= r


    # we know that the rectangle is always horizontal,
    # so we can use the simple test for our purpose
    @classmethod
    def pointInRectangle(point, rectangle):
        (X, Y) = point
        (A,B,C,D) = rectangle

        return (X > A and X < C and Y > D and Y < B)

