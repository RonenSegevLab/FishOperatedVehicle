#!/usr/bin/env python
# license removed for brevity


import rospy
import numpy as np
import pandas as pd
import cv2 as cv
import matplotlib.pyplot as plt
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image


class calibration():
	
    def __init__(self):


	self.lower = []
	self.higher =[]

	self.start = False

	self.bridge = CvBridge()

        rospy.init_node('calibration', anonymous=True)
        rospy.Subscriber("usb_cam/image_raw", Image, self.callback_cam)
	rate = rospy.Rate(10) # 10 Hz


	cal = pd.read_csv(r'~/catkin_ws/src/FishFollow/set/cal.csv')
	lower_hsv, higher_hsv =  np.array(cal['lows']) , np.array(cal['highs'])


        cv.namedWindow('image')

        ilowH = lower_hsv[0]
        ihighH = higher_hsv[0]

        ilowS = lower_hsv[1]
        ihighS = higher_hsv[1]

        ilowV = lower_hsv[2]
        ihighV = higher_hsv[2]

        # create trackbars for color change

        cv.createTrackbar('lowH','image',ilowH,179, self.callback)
        cv.createTrackbar('highH','image',ihighH,179, self.callback)

        cv.createTrackbar('lowS','image',ilowS,255, self.callback)
        cv.createTrackbar('highS','image',ihighS,255, self.callback)

        cv.createTrackbar('lowV','image',ilowV,255, self.callback)
        cv.createTrackbar('highV','image',ihighV,255, self.callback)


	rate = rospy.Rate(1) # 10hz

	while not rospy.is_shutdown():

		if self.start:

			#hello_str = "hello world %s" % rospy.get_time()

			# grab the frame
			frame = self.im

			# get track positions
			ilowH = cv.getTrackbarPos('lowH', 'image')
			ihighH = cv.getTrackbarPos('highH', 'image')
			ilowS = cv.getTrackbarPos('lowS', 'image')
			ihighS = cv.getTrackbarPos('highS', 'image')
			ilowV = cv.getTrackbarPos('lowV', 'image')
			ihighV = cv.getTrackbarPos('highV', 'image')

			hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

			self.lower = [ilowH, ilowS, ilowV]
			self.higher = [ihighH, ihighS, ihighV]	

			mask = cv.inRange(hsv, np.array(self.lower), np.array(self.higher))

			frame = cv.bitwise_and(frame, frame, mask=mask)

			HSV = {'lows': self.lower,
			'highs': self.higher
			}

			df = pd.DataFrame(HSV, columns= ['lows', 'highs'])
			df.to_csv(r'~/catkin_ws/src/FishFollow/set/cal.csv')

			# show thresholded image
			cv.imshow('image', frame)

			k = cv.waitKey(1000) & 0xFF # large wait time to remove freezing

			if k == 113 or k == 27:break



    def callback_cam(self, data):
                
            try:        
                self.im = self.bridge.imgmsg_to_cv2(data, desired_encoding="bgr8")
		self.start = True
   
            except CvBridgeError, e:
                 print e


    def callback(x,y):
        pass




if __name__ == '__main__':

    print ("image calibration")
    rec = calibration() 
    rospy.spin()
