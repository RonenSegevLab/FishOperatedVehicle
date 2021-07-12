#!/usr/bin/env python
# license removed for brevity

import rospy
import numpy as np
from geometry_msgs.msg import Twist
import sys, select, termios, tty

class moveMotors():
    
    def __init__(self):

        self.start = False

        self.twist = Twist()

        self.twist.angular.x = 0; self.twist.angular.y = 0; self.twist.angular.z = 0; self.twist.linear.z = 0

        self.U = 0
        self.V = 0 
        self.k = 0

        pub = rospy.Publisher('M0M1', Twist, queue_size = 1)
        rospy.init_node('mControl', anonymous=True)
        rospy.Subscriber("mouse_vel", Twist, self.callback_ve)
       
        self.rate = rospy.Rate(1) # ROS Rate at 5Hz


        while not rospy.is_shutdown():
            
            if self.start:

                if self.k < self.UU.shape[0]:
                    self.U = np.float32(self.UU[self.k])
                if self.k < self.VV.shape[0]:
                    self.V = np.float32(self.VV[self.k])

                self.twist.linear.x = self.U; self.twist.linear.y = self.V
                pub.publish(self.twist)

                self.k= self.k+1
                rospy.sleep(0.05)


    def callback_ve(self, data):

        V = 60
        self.k = 0

        num_u = abs(data.linear.x*V -self.U)
        num_v = abs(data.linear.y*V -self.V)

        self.UU = np.linspace(self.U , data.linear.x*V , num = num_u/3)
        self.VV = np.linspace(self.V , data.linear.y*V , num = num_v/3)
        self.start = True


    def callback_ve2(self, data):

        num_u = abs(data.linear.x -self.U)
        num_v = abs(data.linear.y-self.V)

        num = max(num_u,num_v)

        UU = np.linspace(self.U , u , num = num_u)
        VV = np.linspace(self.V , v , num = num_v)

        UV =  np.concatenate((UU, VV), axis=0)
        UV = UV.reshape(2,int(num_u))

        for i,j in UV.T:

            self.U = np.float32(i)
            self.V = np.float32(j)
            self.twist.linear.x = i; self.twist.linear.y = j 
            self.pub.publish(self.twist)
            rospy.sleep(0.01)
           

if __name__ == '__main__':

    print 'Node mControl start'
    PFtry = moveMotors() 
    rospy.spin()
