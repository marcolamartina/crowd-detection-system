#!/usr/bin/env python3
import numpy as np
import rospy
import math
from std_msgs.msg import String
from nav_msgs.msg import Odometry as Odometry_msg
from scipy.spatial.transform import Rotation
import rosservice

def distance(p1,p2):
    return np.hypot(p1[0]-p2[0],p1[1]-p2[1])

def math_distance(p1,p2):
    return math.hypot(p1[0]-p2[0],p1[1]-p2[1])

def loginfo(text):
    rospy.loginfo(text)

def logerr(text):
    rospy.logerr(text)

def debug(text):
    return
    #rospy.logwarn(text)

def publish_interaction(topic, message): 
    rate = rospy.Rate(10) # 10hz
    pub = rospy.Publisher('/interaction_node/'+topic, String, queue_size=10)
    msg = String()
    msg.data=message
    pub.publish(msg)
    rate.sleep()

def publish_odometry(topic, x, y, theta): 
    rate = rospy.Rate(10) # 10hz
    pub = rospy.Publisher('/odometry_node/'+topic, Odometry_msg, queue_size=10)
    msg = Odometry_msg()
    msg.pose.pose.position.x=x
    msg.pose.pose.position.y=y
    msg.pose.pose.position.z=theta 
    pub.publish(msg)
    rate.sleep()


def call_service(robot_name,device_name,service_name,*args):
        service_string = "/%s/%s/%s" % (robot_name, device_name, service_name)
        rospy.loginfo(service_string)
        rospy.wait_for_service(service_string)
        try:
            service = rospy.ServiceProxy(service_string,rosservice.get_service_class_by_name(service_string))
            response = service(*args)
            rospy.loginfo("Service %s called" % service_string)
            return response
        except rospy.ServiceException as e:
            utils.logerr("Service call failed: %s" % e)    

