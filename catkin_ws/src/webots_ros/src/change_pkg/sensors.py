#!/usr/bin/env python3
import math
from scipy.spatial.transform import Rotation
import numpy as np
import cv2

class Sensors:
    def __init__(self, robot):
        self.lidar =            LidarSensor("Hokuyo_URG_04LX_UG01",True,robot,240,5.58)
        self.accelerometer =    MovementSensor("accelerometer",True,robot)
        self.bumper =           Sensor("base_cover_link",True,robot)
        self.sonar_01 =         Sensor("base_sonar_01_link",False,robot)
        self.sonar_02 =         Sensor("base_sonar_02_link",False,robot)
        self.sonar_03 =         Sensor("base_sonar_03_link",False,robot) 
        self.battery =          Sensor("battery_sensor",False,robot)
        self.camera =           Sensor("camera",True,robot)
        self.gyro =             MovementSensor("gyro",True,robot)    
        self.head_horizontal =  Sensor("head_1_joint_sensor",True,robot)
        self.head_vertical =    Sensor("head_2_joint_sensor",True,robot)
        self.inertial_unit =    Sensor("inertial_unit",False,robot)
        self.joystick =         Sensor("joystick",False,robot)
        self.keyboard =         Sensor("keyboard",False,robot)
        self.torso =            Sensor("torso_lift_joint_sensor",True,robot)
        self.left_wheel =       Sensor("wheel_left_joint_sensor",True,robot)
        self.right_wheel =      Sensor("wheel_right_joint_sensor",True,robot)


    def init(self,time_step):
        for key, sensor in vars(self).items():
            if sensor.active and key!='robot':
                sensor.init(time_step)
    def get_device_name(self, device):
        for key, sensor in vars(self).items():
            if sensor.name == device:
                return key    

class Sensor:
    def __init__(self, name, active, robot):                    
        self.name = name
        self.active = active
        self.value = None
        self.__robot = robot

    def init(self,time_step):
        self.__robot.call_service(self.name,"enable",time_step)

    def inertial_unit_callback(self, values):      
        q = values.orientation
        rot = Rotation.from_quat([q.x,q.y,q.z,q.w])
        rot_euler = rot.as_euler('xyz', degrees=True) 
        self.value = 180*rot_euler[2]/math.pi



    def camera_callback(self, values):
        image = np.ndarray(shape=(values.height, values.width, 4),
                dtype=np.dtype('uint8'), buffer=values.data)
        size = image.shape
        if size[0] > 1 and size[1] > 1:
            self.value = cv2.cvtColor(image.copy(),cv2.COLOR_RGBA2RGB)
        else:
            self.value = None
        #cv2.imshow('frame',image)
        #cv2.waitKey(1)

    def motor_sensor_callback(self, values):
        return values.data  

    def head_1_joint_sensor_callback(self, values):
        self.value = self.motor_sensor_callback(values)

    def head_2_joint_sensor_callback(self, values):
        self.value = self.motor_sensor_callback(values)   

    def wheel_left_joint_sensor_callback(self, values):
        self.value = self.motor_sensor_callback(values)
        
    def wheel_right_joint_sensor_callback(self, values):
        self.value = self.motor_sensor_callback(values)

    def torso_lift_joint_sensor_callback(self, values):
        self.value = self.motor_sensor_callback(values) 

    def Hokuyo_URG_04LX_UG01_callback(self, values):
        section=24
        point_increment = math.floor(len(values.ranges)/section)
        angle_increment = math.floor(self.fov/section)
        self.value = [(min(values.ranges[i*point_increment:(i+1)*point_increment]),i*angle_increment+math.floor(angle_increment/2-self.fov/2)) for i in range(section)]

    def base_cover_link_callback(self, values):
        self.value = values.data    


    

class MovementSensor(Sensor):
    def __init__(self, name, active, robot):
        super().__init__(name, active, robot)
        self.value=Vector()

    def accelerometer_callback(self, values):
        self.value.x=values.linear_acceleration.x
        self.value.y=values.linear_acceleration.y
        self.value.z=values.linear_acceleration.z
        self.value.t=values.header.stamp

    def gyro_callback(self, values):
        self.value.x=values.angular_velocity.x
        self.value.y=values.angular_velocity.y
        self.value.z=values.angular_velocity.z
        self.value.t=values.header.stamp

class LidarSensor(Sensor):
    def __init__(self, name, active, robot, fov, range_max):
        super().__init__(name, active, robot)
        self.fov=fov
        self.range_max=range_max       


class Vector:
    def __init__(self,x=0,y=0,z=0,t=0):
        self.x=x
        self.y=y
        self.z=z
        self.t=t

    def __str__(self):
        return "x:{} y:{} z:{} t:{}".format(self.x,self.y,self.z,self.t)

    def copy(self):
        return Vector(self.x,self.y,self.z,self.t)

