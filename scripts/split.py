#!/usr/local/bin/python
import os
import cv2, imutils
import numpy as np

# sequence number for file naming
seq = 0

def rotate_image(image, center, angle):
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

def processFile(filePath):
    print("processing "+filePath)
    global seq
    #cv2.namedWindow('image', cv2.WINDOW_NORMAL)

    image = cv2.imread(filePath)
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

    # already processed image centers
    processed = set()

    # process each possible photo
    for c in cnts:
        # extract tuple with (center, dimensions, angle)
        rect = cv2.minAreaRect(c)

        image_center = rect[0]
        int_image_center = (int(image_center[0]), int(image_center[1]))

        # ignore this rect if already processed
        if int_image_center in processed: continue
        else: processed.add(int_image_center)    

        # extract box
        box = cv2.cv.BoxPoints(rect) if imutils.is_cv2() else cv2.boxPoints(rect)
        box = np.array(box, dtype="int")

        # ignore small elements
        if cv2.contourArea(box) < 1000000: continue

        print("\t"+str(image_center))

        image_width = int(rect[1][1])
        image_height = int(rect[1][0])

        # images turned a little to the right are corrected
        angle = rect[2]
        if angle < 45: 
            angle = 90+angle
            image_width = int(rect[1][0])
            image_height = int(rect[1][1])

        rotated = rotate_image(image, image_center, angle-90)

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
        cv2.imwrite("images/image"+str(seq)+".jpg", crop_img)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        

        #####

        #bgr = cv2.imread("image"+str(seq)+".jpg")
        #lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        #lab_planes = cv2.split(lab)
        #clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
        #lab_planes[0] = clahe.apply(lab_planes[0])
        #lab = cv2.merge(lab_planes)
        #bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        #####

        seq += 1

    #cv2.imshow("Image", image)
    #cv2.waitKey(0)

def processDirectory(path):
    directory = os.fsencode(path)
    
    for file in sorted(os.listdir(directory), key=len):
        filename = os.fsdecode(file)
        if filename.endswith(".jpg") or filename.endswith(".jpeg"): 
            processFile(os.path.join(path, filename))
            #print(os.path.join(path, filename))
        else:
            continue

processDirectory("/Volumes/crypto/et_photos/scanned/")

#processFile(/Volumes/crypto/et_photos/scanned/Scan.jpeg)