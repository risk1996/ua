import cv2
import numpy

def sigmoid(x):
    return 1/(1+numpy.exp(-x))

def accuracy(x):
    return int(round(2*(sigmoid(x)-.5)*100))

# PosLowBound = numpy.array([  5,  80,  40])
# PosUppBound = numpy.array([ 30, 255, 255])
# NegLowBound = numpy.array([ 85,  80,  40])
# NegUppBound = numpy.array([ 95, 255, 255])

image = cv2.imread('benedict.png')
# imageHSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
# maskPos  = cv2.inRange(imageHSV, PosLowBound, PosUppBound)
# maskPos[0][0] = 255
# maskNeg  = cv2.inRange(imageHSV, NegLowBound, NegUppBound)
# maskNeg[0][0] = 255
# unique, countsPos = numpy.unique(maskPos, return_counts=True)
# unique, countsNeg = numpy.unique(maskNeg, return_counts=True)
# print(accuracy(5*(countsPos[1]-countsNeg[1])/(numpy.sum(countsPos))))
# cv2.imshow("mask+", maskPos)
# cv2.imshow("mask-", maskNeg)
cv2.imshow("cam", image)
cv2.waitKey(1000000)