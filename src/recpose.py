#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
import numpy as np
import pandas as pd
from time import gmtime, strftime
from geometry_msgs.msg import Twist


class recPose():
	
    def __init__(self):

        rospy.init_node('recPose', anonymous=True)
        self.tStart = rospy.get_time()

	self.pose = []
	self.t = []
	
	self.Xrobot = []
	self.Yrobot = []
	self.YAWrobot = []
	self.poles = []
	self.obsticals = []   
   
 	self.Xfish = []
	self.Yfish = []
	self.YAWfish = []
	self.FishPose =  PoseStamped()
	self.startP = False
	self.pole = 0
	self.recRate = 0
	self.obsitcaleAvoid = 0
	self.isVel = 0


	rospy.Subscriber("slam_out_pose", PoseStamped, self.callbackR)
	rospy.Subscriber('fishPose', PoseStamped, self.callbackF)
	rospy.Subscriber('cmd_vel', Twist, self.callbackPole)
	
 
	strtime = strftime("%Y_%m_%d__%H:%M:%S", gmtime())
	self.loc = r'~/PoseRec/fish_pose$' + strtime + r'.csv'


    def callbackR(self, data):

		#if (self.recRate%1 == 0):

		self.t.append(rospy.get_time()-self.tStart) # time 
		self.Xrobot.append(data.pose.position.x) #robot position
		self.Yrobot.append(data.pose.position.y)
		self.YAWrobot.append(data.pose.orientation.z)
		self.poles.append(self.pole)
		self.obsticals.append(self.obsitcaleAvoid)
		

		if self.startP: # In case the fish is navigate the robot -> keep fish position data

			self.Xfish.append(self.FishPose.pose.position.x) #fish position
			self.Yfish.append(self.FishPose.pose.position.y)
			self.YAWfish.append(self.FishPose.pose.position.z)
			

		else: # else set fish position to zero 

			self.Xfish.append(0) #fish position
			self.Yfish.append(0)
			self.YAWfish.append(0)
			

		Pose = {
		't':self.t,
		'Xr': self.Xrobot,
		'Yr': self.Yrobot,
		'YAWr': self.YAWrobot,
		'Xf': self.Xfish,
		'Yf': self.Yfish,
		'YAWf': self.YAWfish,
		'velCom': self.poles,
		}
			
		df = pd.DataFrame(Pose, columns= ['t' , 'Xr', 'Yr' , 'YAWr' , 'Xf', 'Yf' , 'YAWf', 'velCom']) #save position data
		df.to_csv(self.loc)

#		self.recRate = self.recRate +1 

    def callbackF(self, data):
		self.FishPose = data
		self.startP = True

    def callbackPole(self, data):
		self.pole = data.linear.z 



if __name__ == '__main__':

    print ("start recording")
    rec = recPose() 
    rospy.spin()
