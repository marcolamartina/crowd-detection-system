#!/usr/bin/env python

import change_pkg.path_planning as path_planner
import change_pkg.utils as utils
import itertools
import numpy as np

class Controller:
    def __init__(self, robot):
        self.__robot=robot
        self.scheduler=Scheduler()
        self.path_planner = path_planner.Path_planner(robot)
        self.loop_point= None
        self.LOOKBACK_WINDOW_SIZE = 4
        self.LOOP_PRECISION = 0.1
        self.ESCAPING_DISTANCE = 2
        self.TARGET_DISTANCE = 0.5

    def start(self):
        while(True):
            self.exploration()
            self.go_to_gathering()
            self.__robot.warning()
            #self.__robot.odometry.movement_history()


    def go_to_gathering(self):
        self.scheduler.potential_field_mode()
        while self.path_planner.target_distance() > self.TARGET_DISTANCE:
            self.schedule_movement()
            self.set_mode()
        self.__robot.movement.rotate(-self.path_planner.target_angle())  


    def exploration(self):
        self.scheduler.exploration_mode()
        valid_target = False
        while not valid_target:
            self.exploration_movement()
            self.__robot.movement.scan()
            valid_target = self.path_planner.set_target(self.path_planner.find_clusters(self.__robot.vision.locate_targets()))

        

    def schedule_movement(self):
        mode=self.scheduler.get_mode()
        if mode == 'bug':
            self.bug_movement()
        elif mode == 'potential_field':
            self.potential_field_movement()



    def set_mode(self):
        mode=self.scheduler.get_mode()
        if mode == 'bug':
            distance = utils.distance((self.__robot.odometry.x,self.__robot.odometry.y),self.loop_point)
            if distance > self.ESCAPING_DISTANCE:
                self.scheduler.potential_field_mode() 
        elif mode == 'potential_field' and self.check_loop():
            self.scheduler.bug_mode()  


    def check_loop(self):
        """
        :returns: True if the robot is in a loop, False otherwise

        """
        position_loop=False
        point_list= [(x,y) for ((x,y),_distance) in self.__robot.odometry.history[0:self.LOOKBACK_WINDOW_SIZE]]
        for point_couple in itertools.combinations(point_list,2):
            if utils.distance(point_couple[0],point_couple[1])<self.LOOP_PRECISION:
                position_loop=True
                self.loop_point=point_couple[0]
                break
        rotation_loop = self.__robot.odometry.history[0][1] - self.__robot.odometry.history[self.LOOKBACK_WINDOW_SIZE-1][1]  < 0.1
        if rotation_loop:
            self.loop_point= self.__robot.odometry.history[0][0]  
        return rotation_loop or position_loop

    def bug_movement(self):
        distance,angle = self.path_planner.bug_next_step()
        self.__robot.movement.rotate(angle)
        self.__robot.movement.move_forward(distance)

    def exploration_movement(self):
        distance,angle = self.path_planner.exploration_next_step()
        self.__robot.movement.rotate(angle)
        self.__robot.movement.move_forward(distance)    

    def potential_field_movement(self):
        angle = self.path_planner.next_step_direction()
        self.__robot.movement.rotate(angle)
        distance=self.path_planner.movement_distance()
        self.__robot.movement.move_forward(distance)


class Scheduler:
    def __init__(self):
        self.bug=False
        self.potential_field=False
        self.exploration=True

    def bug_mode(self):
        self.bug=True
        self.potential_field=False
        self.exploration=False

    def potential_field_mode(self):
        self.bug=False
        self.potential_field=True
        self.exploration=False 

    def exploration_mode(self):
        self.bug=False
        self.potential_field=False
        self.exploration=True

    def get_mode(self):
        for mode, flag in vars(self).items():
            if flag:
                return mode                       