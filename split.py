#!/usr/local/bin/python
from os import abort
import cv2, sys, imutils
import numpy as np

def rotate_image(image, center, angle):
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

def process():
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)

    image = cv2.imread("image.jpg")
    ratio = image.shape[0] / 300.0
    image = imutils.resize(image, height = 1000)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    ret, th = cv2.threshold(gray,220,235,1)
    edged = cv2.Canny(th, 25, 200)

    cnts, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE,   cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)

    for c in cnts:
        rect = cv2.minAreaRect(c)

        box = cv2.cv.BoxPoints(rect) if imutils.is_cv2() else cv2.boxPoints(rect)
        box = np.array(box, dtype="int")
        if cv2.contourArea(box) > 70000:
            rotated = rotate_image(image, rect[0], 90-rect[2])
            cv2.drawContours(image, [box], -1, (0, 255, 0), 2)

            cv2.imshow("Image", rotated)
            cv2.waitKey(0)

    #cv2.imshow("Image", image)
    #cv2.waitKey(0)

process()