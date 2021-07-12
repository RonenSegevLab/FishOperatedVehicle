#!/usr/bin/env python
# license removed for brevity

import rospy
import Tkinter 
import pandas as pd

from sensor_msgs.msg import Image
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Twist

import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from cv_bridge import CvBridge, CvBridgeError


import sys, select, termios, tty

import matplotlib.pyplot as plt



class fishBot():
    
    def __init__(self):

        #self.writer= cv.VideoWriter('fish.mp4', cv2.VideoWriter_fourcc(*'DIVX'), 20, (width,height))
        self.count =0
        self.firstFrame = True
        self.started = False
        self.bridge = CvBridge()
        self.im = None

        self.u = 0
        self.v = 0 
        self.fgbg = cv.createBackgroundSubtractorKNN() 

        self.check = True
        self.deltaX = 200
        self.X1b = 0
        self.X1c = 0
        self.theta = 0
        self.cmax = None
        self.extBot2 = None

        self.V = 70
        self.twist = Twist()
        self.twist.linear.x = 0; self.twist.linear.y = 0; self.twist.linear.z = 0
        self.twist.angular.x = 0; self.twist.angular.y = 0; self.twist.angular.z = 0
        
	self.scale = 0.0014 # frome fish pose (pixle) to m

	#Recoreded data
	self.pubFishPose = rospy.Publisher('fishPose', PoseStamped, queue_size = 1)
	self.posemsg = PoseStamped()


        ## collabration data
	cal = pd.read_csv(r'~/catkin_ws/src/FishFollow/set/cal.csv')
	self.lower_hsv, self.higher_hsv =  np.array(cal['lows']) , np.array(cal['highs'])

        rospy.init_node('Robofish', anonymous=True)

        self.pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
        rospy.Subscriber("usb_cam/image_raw", Image, self.callback_cam)


        #creat array of regions seprated by segments in radians
        self.radArr = np.linspace(0,   1.5 * np.pi  , 4 )
        radios = 200
        self.circle = np.array([np.cos(self.radArr)*radios +160 , np.sin(self.radArr)*radios+ 120])

        
    def callback_cam(self, data):
        
        # Use cv_bridge() to convert the ROS image to OpenCV format
                
	try:        
		cv_image = self.bridge.imgmsg_to_cv2(data, desired_encoding="bgr8")
		self.im = cv_image
		dir = self.find_dir()

	    
    	except CvBridgeError, e:

		print e



    def find_dir(self):

        frame = self.im

        if frame is None: return True
            
        # Every color except white
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, self.lower_hsv, self.higher_hsv)
        result = cv.bitwise_and(frame, frame, mask=mask)
        fgmask = self.fgbg.apply(result)
        
        _, th1 = cv.threshold(result, 30, 255 , cv.THRESH_BINARY)
        gray = 255 -  cv.cvtColor(th1, cv.COLOR_BGR2GRAY)

        # Find outer contours
        image, cnts, hierarchy = cv.findContours(gray, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        areaSUM, CCy , CCx , maxA , CxMax , CyMax ,maxC ,c = 0 , 0 ,0 ,0, 0 ,0,0,None

        for c in cnts:
            
            M = cv.moments(c)
            if  M['m00'] > 500 :

                cx = int(M['m10']/M['m00']) # x c.m
                cy = int(M['m01']/M['m00']) # y c.m
                areaSUM  = areaSUM + M['m00'] # sum over Ai
                CCx = CCx  + cx* M['m00'] # sum over x c.m
                CCy = CCy + cy*M['m00']# sum over y c.m

                if maxA < M['m00']: maxA  ,CxMax , CyMax , self.cmax = M['m00'] , cx ,cy ,c

        if areaSUM > 0 :CCx , CCy  = CCx / areaSUM ,CCy / areaSUM
        Xc = tuple(np.array([CCx, CCy], dtype= int).reshape(1, -1)[0])
        Xcmax = tuple(np.array([CxMax, CyMax], dtype= int).reshape(1, -1)[0])
        #cv.circle(frame, Xcmax, 10, (0, 0, 255), -1)
        
        extBot = 0 
        if  maxA >= 0.9 * areaSUM: #and areaSUM > 1200 and areaSUM<2000:
            
            if not not np.shape(c) and not not np.shape(self.cmax):
                # determine the most extreme points along the contour
                argmaxdist = np.argmax(np.matmul(np.array(np.power((self.cmax - Xc),2) ), [1,1]))
                self.extBot2 =  tuple(self.cmax[argmaxdist,0])
                cv.circle(frame, self.extBot2, 10, (0, 255, 255), -1)
                cv.arrowedLine(frame, self.extBot2, Xc, (0, 255, 0), 2, tipLength=0.2)
                self.setV(Xc, self.extBot2)

        cv.drawContours(frame, cnts, -1, (255 ,0, 0), 2)
        cv.imshow('arrow', frame)

        cv.imwrite("~/PoseRecNew/pics/frame%d.jpg" % self.count, frame)   # save frame as JPEG file
        self.count +=1      

        key = cv.waitKey(30)
        if key == 'q' or key == 27: return True

        return False

    def setV(self , Cm , Cr):
        # foind the length of the fish to avoid system noise
        fishLength = np.matmul(np.power(np.array(Cm)- np.array(Cr),2),(1,1))


	if fishLength < 20000:

                slope =  np.array(Cm) - np.array(Cr)  
                theta = np.arctan2(slope[1],slope[0]) 
                fishPose = np.array([Cm[0], Cm[1]])
                dist = np.matmul(np.power(self.circle.T -fishPose,2) ,(1,1))

                fishRigion = np.argmin(dist)
                #print fishRigion

                if fishRigion ==  0: angleOfRigion = 0 
                if fishRigion ==  1: angleOfRigion = 90
                if fishRigion ==  2: angleOfRigion = 170
                if fishRigion ==  3: angleOfRigion = 260

                anglediff = (np.rad2deg(theta) - angleOfRigion + 180 + 360) % 360 - 180

                #print anglediff

                self.posemsg.pose.position.x = (fishPose[0]-160)*self.scale # x position
                self.posemsg.pose.position.y = -1*(fishPose[1]-120)*self.scale # y position
                self.posemsg.pose.position.z = theta # YAW

                #print self.posemsg.pose.position

                #publish fish position 
                self.pubFishPose.publish(self.posemsg)

                if (anglediff <= 100 and anglediff>=-100):

                        u = np.cos(theta)*self.V
                        v = np.sin(theta)*self.V*-1

                else: u,v = 0 , 0


	else: u,v = 0 , 0


        #print fishRigion , 'vilocity' , u , v ,'FishPose' ,fishPose ,'angle', np.rad2deg(theta) ,theta ,anglediff
        self.twist.linear.x = v; self.twist.linear.y = -u ;self. twist.linear.z = self.theta
        self.pub.publish(self.twist)
        
if __name__ == '__main__':

    print "ok"
    PFtry = fishBot() 
    rospy.spin()
