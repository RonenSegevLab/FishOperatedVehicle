#!/usr/bin/env python

import rospy
import math
import numpy as np
from time import gmtime, strftime
from geometry_msgs.msg import Twist
import sys, select, termios, tty
from sensor_msgs.msg import LaserScan
import pandas as pd

class laserScanner():
    
    def __init__(self):
        
        rospy.init_node('laserRec', anonymous=True)
        self.tStart = rospy.get_time()
        self.t = []    
        self.odeg = []
        self.ldeg = []
        self.jdeg = []
        self.ndeg = []
        self.poles = []
        self.pole = 0
        self.start_laser = False

        rospy.Subscriber('/scan', LaserScan, self.callback_laser)
        rospy.Subscriber('cmd_vel', Twist, self.callbackPole)

        self.rate = rospy.Rate(100) # ROS Rate at 1Hz

	strtime = strftime("%Y_%m_%d__%H:%M:%S", gmtime())
	self.loc = r'~/distRec/robotDist$' + strtime + r'.csv'

    def callback_laser(self,msg):

        self.t.append(rospy.get_time()-self.tStart) # time 
        o = np.array(msg.ranges[350:360])
        l = np.array(msg.ranges[85:95])
        j = np.array(msg.ranges[175:185])
        n = np.array(msg.ranges[265:275])
        
        print(np.mean(o[o<100]))
        self.odeg.append(np.mean(o[o<100]))
        self.ldeg.append(np.mean(l[l<100]))
        self.jdeg.append(np.mean(j[j<100]))
        self.ndeg.append(np.mean(n[n<100]))
        
        self.poles.append(self.pole)
        
        Pose = {'t':self.t,
        '0deg':self.odeg,
        '90deg':self.ldeg,
        '180deg':self.jdeg,
        '270deg':self.ndeg,
        'start':self.poles}
        
        df = pd.DataFrame(Pose, columns= ['t','0deg','90deg','180deg','270deg','start']) #save position data
        df.to_csv(self.loc)

    def callbackPole(self, data):
	    	self.pole = data.linear.z 


if __name__ == '__main__':

    print ('Laser scanner is on')
    PFtry = laserScanner() 
    rospy.spin()
