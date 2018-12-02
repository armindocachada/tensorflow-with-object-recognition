import datetime
import re
import os

import ephem

charlton = ("51.4818", "0.0402")



class VideoUtils(object):

    @classmethod
    def extractTimestamp(cls,filePath):
        result = datetime.datetime.now()

        # for simplicity we will extract time video was created from filename
        # we could also extract it from the metainformation in the video, but
        # that would be harder.
        matches = re.match("\w+_(\d+).mp4", os.path.basename(filePath))
        if matches:
            epoch = matches.group(1)
            result = datetime.datetime.fromtimestamp(float(epoch))

        print(filePath)
        return result

    # determines if video was recorded after sunset.
    # currently we do this by analysing timestamp and using ephem library
    # to determine if the video was recorded after sunset.
    @classmethod
    def isAfterSunset(cls, filePath):
        timestamp = cls.extractTimestamp(filePath)
        # for now location is fixed to charlton
        sunup = cls.isSunup(charlton, timestamp)
        print ("timestamp is %s sunup: %s and not sunup %s" % (timestamp,sunup, not sunup))
        return not sunup

    # daytime depends on the season, time of the year, etc
    @classmethod
    def isSunup(cls, coordinates, time):
       (lat, long) = coordinates
       o = ephem.Observer()
       o.long = long
       o.lat = lat
       o.date = time
       s = ephem.Sun()
       s.compute(o)
       return s.alt > 0


    @classmethod
    def overlap(cls, r1, r2):
        '''Overlapping rectangles overlap both horizontally & vertically
        '''
        (a1, b1, c1, d1) = r1
        (a2, b2, c2, d2) = r2

        left_r1 = min(a1,c1)
        left_r2 = min(a2,c2)
        right_r1 = max(a1,c1)
        right_r2 = max(a2,c2)

        top_r1 = max(b1,d1)
        bottom_r1 = min(b1,d1)

        top_r2 = max(b2,d2)
        bottom_r2 = min(b2,d2)

        result = cls.range_overlap(left_r1, right_r1, left_r2, right_r2) and \
                 cls.range_overlap(bottom_r1, top_r1, bottom_r1, top_r2)
        print("(a1,b1,c1,d1)=(%d,%d,%d,%d)" % (a1, b1, c1, d1))
        print("(a2,b2,c1,d1)=(%d,%d,%d,%d)" % (a2, b2, c2, d2))

        print("Overlap %s" % result)
        return result


    @classmethod
    def range_overlap(cls, a_min, a_max, b_min, b_max):
        '''Neither range is completely greater than the other
        '''
        return (a_min <= b_max) and (b_min <= a_max)