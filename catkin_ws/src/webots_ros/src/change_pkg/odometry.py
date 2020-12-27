#!/usr/bin/env python
import rospy
import math
import numpy as np
import matplotlib.pyplot as plt


class Odometry:
    def __init__(self):
        self.history=[[0,0]]
        self.x=0
        self.y=0
        self.theta=0
        self.distance_traveled = 0

    def update_position(self, distance):
        self.distance_traveled = self.distance_traveled \
                + np.hypot(distance[0], distance[1])
        self.x = self.x + distance[1]*math.cos(math.pi*self.theta/180) - distance[0]*math.sin(math.pi*self.theta/180)
        self.y = self.y + distance[1]*math.sin(math.pi*self.theta/180) + distance[0]*math.cos(math.pi*self.theta/180)
        self.history.append([self.x, self.y])

    def update_theta(self, theta):
        self.theta = (self.theta + theta) % 360
        self.theta = self.theta if self.theta <= 180 else self.theta -360

    def movement_history(self):
        plt.plot([x for [x,y] in self.history], [y for [x,y] in self.history]) 
        plt.grid(True)
        plt.show()    

    def abs_cartesian_to_polar(self, p):
        """Accepts a point given in cartesian coordinates relative to the world
        frame of reference and converts it to polar coordinates in the robot
        frame of reference based on the current position estimate

        :p:   Cartesian coordinates in the (x, y) format
        :returns:  Cartesian coordinates in the (Rho, Theta) format

        """
        x = p[0] - self.x
        y = p[1] - self.y
        angle = -180/math.pi*math.atan2(x,y)-self.theta
        angle = angle if angle > -180 else angle +360
        return (np.hypot(x,y), angle)


    def polar_to_abs_cartesian(self, p):
        """Accepts a point given in polar coordinates relative to the robot
        frame of reference and converts it to cartesian coordinates in a wolrd
        frame of reference based on the current position estimate

        :p:   Polar coordinates in the (Rho, Theta) format
        :returns:       Cartesian coordinates

        """
        angle=p[1]+self.theta
        return (self.x+p[0]*math.sin(math.pi*angle/180),
                self.y+p[0]*math.cos(math.pi*angle/180))


    def __str__(self):
        return "x:{:.2f} y:{:.2f} theta:{:.2f}".format(self.x,self.y,self.theta)  


