#!/usr/local/bin/python
from os import abort
import cv2, sys, imutils
import numpy as np

def rotate_image(image, center, angle):
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

def process():
    #cv2.namedWindow('image', cv2.WINDOW_NORMAL)

    image = cv2.imread("image.jpg")
    #image = imutils.resize(image, height = 1000)

    # convert to gray
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # canny edge detector
    ret, th = cv2.threshold(gray,220,235,1)
    edged = cv2.Canny(th, 25, 200)

    # find contours
    cnts, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE,   cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)

    seq = 0

    # process each possible photo
    for c in cnts:
        # extract tuple with (center, dimensions, angle)
        rect = cv2.minAreaRect(c)

        # extract box
        box = cv2.cv.BoxPoints(rect) if imutils.is_cv2() else cv2.boxPoints(rect)
        box = np.array(box, dtype="int")

        # discard small elements
        if cv2.contourArea(box) > 70000:
            # draw circle in center
            #cv2.circle(image, (int(rect[0][0]), int(rect[0][1])), 10, (0,0,255), -1)

            image_center = rect[0]
            print(image_center)
            image_width = int(rect[1][1])
            image_height = int(rect[1][0])

            rotated = rotate_image(image, image_center, rect[2]-90)

            corrected_rect = (rect[0], rect[1], -90)
            corrected_box = cv2.cv.BoxPoints(corrected_rect) if imutils.is_cv2() else cv2.boxPoints(corrected_rect)
            corrected_box = np.array(corrected_box, dtype="int")

            # draw green square around image
            #cv2.drawContours(rotated, [corrected_box], -1, (0, 255, 0), 2)

            y_origin = int(image_center[1] - image_height/2)
            x_origin = int(image_center[0] - image_width/2)

            # draw first corner
            #cv2.circle(image, (x_origin, y_origin), 6, (255,0,0), -1)

            crop_img = rotated[y_origin:y_origin+image_height, x_origin:x_origin+image_width]
            #cv2.imshow("image", crop_img)
            ##cv2.imshow("Image", rotated)
            #cv2.waitKey(0)
            cv2.imwrite("image"+str(seq)+".jpg", crop_img)
            seq += 1

    #cv2.imshow("Image", image)
    #cv2.waitKey(0)

process()