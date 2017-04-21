from __future__ import absolute_import, print_function, division
from pymba import *
import numpy as np
import cv2, time

cv2.namedWindow("Camera 1")
cv2.namedWindow("Camera 2")

with Vimba() as vimba:
    system = vimba.getSystem()
    system.runFeatureCommand("GeVDiscoveryAllOnce")
    time.sleep(0.2)
    camera_ids = vimba.getCameraIds()

    for cam_id in camera_ids:
        print("Camera found: ", cam_id)
    print("Camera 1:", camera_ids[0])
    print("Camera 2:", camera_ids[1])
    c0 = vimba.getCamera(camera_ids[0])
    c0.openCamera()
    #print(c0.AcquisitionMode)
    c0.AcquisitionMode = 'SingleFrame'

    c1 = vimba.getCamera(camera_ids[1])
    c1.openCamera()
    #print(c1.AcquisitionMode)
    c1.AcquisitionMode = 'SingleFrame'

    ## set pixel format
    #c0.PixelFormat = "Mono8"
    #c0.ExposureTimeAbs=6000

    frame0 = c0.getFrame()
    frame0.announceFrame()
    c0.startCapture()

    frame1 = c1.getFrame()
    frame1.announceFrame()
    c1.startCapture()

    framecount = 0
    droppedframes = []

    while framecount < 100:
        try:
            frame0.queueFrameCapture()
            success = True
        except:
            droppedframes.append(framecount)
            success = False

        c0.runFeatureCommand("AcquisitionStart")
        c0.runFeatureCommand("AcquisitionStop")
        frame0.waitFrameCapture(1000)
        frame_data0 = frame0.getBufferByteData()

        c1.runFeatureCommand("AcquisitionStart")
        c1.runFeatureCommand("AcquisitionStop")
        frame1.waitFrameCapture(1000)
        frame_data1 = frame1.getBufferByteData()


        if success:
            img0 = np.ndarray(buffer=frame_data0, dtype=np.uint8, shape=(frame0.height, frame0.width, 1))
            #imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgBlurred0 = cv2.GaussianBlur(img0, (5, 5), 0)
            imgCanny0 = cv2.Canny(imgBlurred0, 200, 250)

            img1 = np.ndarray(buffer=frame_data1, dtype=np.uint8, shape=(frame1.height, frame1.width, 1))
            imgBlurred1 = cv2.GaussianBlur(img1, (5, 5), 0)
            imgCanny1 = cv2.Canny(imgBlurred1, 200, 250)

            cv2.imshow("Camera 1", img0)
            cv2.imshow("Camera 2", img1)
        framecount += 1
        #print (framecount)

        k = cv2.waitKey(1)
        if k == 0x1b:
            cv2.destroyAllWindows()
            print("Frames displayed: %i" % framecount)
            print("Frames dropped: %s" % droppedframes)
            break

    c0.endCapture()
    c0.revokeAllFrames()
    c0.closeCamera()

    c1.endCapture()
    c1.revokeAllFrames()
    c1.closeCamera()