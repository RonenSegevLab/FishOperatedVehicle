#!/usr/bin/env python

# -*- coding: utf-8 -*-

"""
Created on Thu Sep  5 10:09:21 2019
@author: Matan Samina
"""

import matplotlib
matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from Tkinter import *

import rospy
import numpy as np
from nav_msgs.msg import OccupancyGrid
from rospy.numpy_msg import numpy_msg
from rospy_tutorials.msg import Floats


class maps:

    def __init__(self , window):

	
        rospy.init_node('change_map_frequancy', anonymous=True)
       


 	window.title('Nav')
        self.fig = Figure(figsize=(6, 6))
        self.a = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=window)
        self.canvas.get_tk_widget().pack()

        self.mapOG = rospy.Subscriber("/map", OccupancyGrid , self.callbackM )

		

    def callbackM(self ,msg):
  
        maps = np.array(msg.data , dtype = np.float32)
        N = np.sqrt(maps.shape)[0].astype(np.int32)
        Re = np.copy(maps.reshape((N,N)))
        
        #convert to landmarks array
        scale = msg.info.resolution
        CenterShift = msg.info.width
        landMarksArray = (np.argwhere( Re == 100 ) * scale) 
 
        #self.mapLM = landMarksArray.astype(np.float32) #-np.array()
	self.plot(landMarksArray[:,0] , landMarksArray[:,1])
 

    def plot(self, x ,v):

        self.a.cla()
        self.a.scatter(x, v, color='black')
	self.a.scatter(51, 51, color='b')


        self.a.set_title ("robofishh map", fontsize=12)

        self.canvas.draw()

def og2lm():

    print ("init     convert map to landmarks")
    window = Tk()    
    LM_maps = maps(window) # convert maps to landmarks arrays
    window.mainloop()
    rospy.spin()

if __name__ == '__main__':

    og2lm()

