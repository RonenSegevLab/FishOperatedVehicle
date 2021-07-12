#!/usr/bin/env python
# license removed for brevity

import rospy
import numpy as np
from geometry_msgs.msg import Twist
import sys, select, termios, tty
from sensor_msgs.msg import LaserScan

class moveMotors():
    
    def __init__(self):

        self.obstical = False
        self.startMove = False

        self.start = False
        self.start_laser = False
        self.twist = Twist()

        self.twist.angular.x = 0; self.twist.angular.y = 0; self.twist.angular.z = 0; self.twist.linear.z = 0

        self.U , self.V ,self.k = 0 , 0 ,0
        self.VV, self.UU = 0 ,0
    
        self.devto = 8
        self.minRanges = [0]*self.devto
        self.minDist = 0.3
        self.laserRange = np.linspace(-np.pi ,np.pi , num = self.devto)

        pub = rospy.Publisher('M0M1', Twist, queue_size = 1)
        rospy.init_node('mControl', anonymous=True)
        rospy.Subscriber("cmd_vel", Twist, self.callback_ve)
        sub = rospy.Subscriber('/scan', LaserScan, self.callback_laser)
       
        self.rate = rospy.Rate(1) # ROS Rate at 1Hz


        while not rospy.is_shutdown():
            
            if self.start:

                if self.k < self.UU.shape[0]:
                    self.U = np.float32(self.UU[self.k])
                if self.k < self.VV.shape[0]:
                    self.V = np.float32(self.VV[self.k])
                        
                if self.start_laser:

                    angle  =  np.arctan2(-1*self.vy ,-1*self.vx) # robot direction
                    argmin_angle_pos =  np.argmin(np.abs(self.laserRange - angle)) # find argument of dir 

                    self.obstical = self.minRanges[argmin_angle_pos]
                    #print(self.obstical)

                    if self.obstical:
			
                        self.stopMotors()
                        self.twist.angular.x = 1

                    else: 
                        self.obstical = False
                        self.twist.angular.x = 0
                        
                    
                    self.twist.linear.x = self.U; self.twist.linear.y = self.V
                    pub.publish(self.twist)
                    self.k= self.k+1

                rospy.sleep(0.05)


    def callback_ve(self, data):

        self.k = 0
        u, v = data.linear.x , data.linear.y
        self.vx , self.vy = u , v

        if not self.obstical:

            num_u , num_v = abs(u -self.U) ,abs(v-self.V)
            self.UU = np.linspace(self.U , u , num = num_u/6)
            self.VV = np.linspace(self.V , v , num = num_v/6)
            self.startMove = True
            self.start = True

    def stopMotors(self):
       
	
        self.k = 0

        u, v = 0 , 0

        num_u , num_v = abs(u -self.U) ,abs(v-self.V)

        self.UU = np.linspace(self.U , u , num = num_u/6)
        self.VV = np.linspace(self.V , v , num = num_v/6)

    def callback_laser(self,msg):
        

        self.dev = np.shape(msg.ranges)[0]/self.devto
        res = tuple(self.grouper(self.dev, msg.ranges)) 
        k = 0

        for i in res:

            temp = np.array(i)
            if  temp.any() < 0.35 : minr = 1000
            else: minr =  min(temp[np.nonzero(temp)])

        minD = self.minDist
        factor = 1.2

        for i in res:

            if k == 0 :  minD = 0.6*factor
            elif k == 1 : minD = 0.4*factor # left
            elif k == 2 : minD = 0.3*factor
            elif k == 3 : minD = 0.3*factor # back 
            elif k == 4 : minD = 0.3*factor
            elif k == 5 : minD = 0.4*factor # rigth
            elif k == 6 : minD = 0.5*factor
            elif k == 7 : minD = 0.5*factor # front 

            temp = np.array(i)
            if  temp.any() < 0.1 : minr = 1000
            else: minr =  min(temp[np.nonzero(temp)])
            
            self.minRanges[k] = minr < minD
            k = k+1
        
        self.start_laser = True
        print self.minRanges

    def grouper(self, n, iterable): 
        args = [iter(iterable)] * n 
        return zip(*args) 

           
if __name__ == '__main__':

    print 'Node mControl start'
    PFtry = moveMotors() 
    rospy.spin()
