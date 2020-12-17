from ros_interface import *
import cv2

angular_velocity = 3.0
linear_velocity  = 3.0

def set_angular_velocity(speed):
    call_service(motors[0], 'set_velocity',-speed*330/2);
    call_service(motors[1], 'set_velocity', speed*330/2);


def set_linear_velocity(speed):
    call_service(motors[0], 'set_velocity', speed);
    call_service(motors[1], 'set_velocity', speed);


def stop():
    set_linear_velocity(0)


def rotate(rotation, precision):
    """
    :rotation:  The desired rotation in degrees. Note that a rotation greater
        than 180° in modulo will be substituted with a rotation in the opposite
    direction.
    :precision: The     maximum difference from the required rotation and the
        actual rotation. If this value is smaller than the sensor noise it makes
        no sense.
    """
    stop()
    curr_angular_velocity = angular_velocity
    direction, framenum=1
    processCallbacks()
    #update_frame()
    #update_object_roi()
    current_angle = get_angle()
    target_angle=rotation+get_angle()
    # adjust for discontinuity at +/-180°
    target_angle =  target_angle-360 if target_angle >  180 else target_angle
    target_angle =  360+target_angle if target_angle < -180 else target_angle
    difference = target_angle-current_angle
    if(difference > 180):
        difference = difference - 360
    elif (difference < -180):
        difference = difference + 360

    direction =  1 if difference > 0 else -1
    while(abs(difference)>precision):
        #update_frame()
        framenum = (framenum+1)%100
        if(framenum == 0):
            if(cv2.waitKey(1) == ' '):
                break

        current_angle = get_angle()
        difference = target_angle-current_angle
        if(difference > 180):
            difference = difference - 360
        elif (difference < -180):
            difference = difference + 360

        if(direction*difference < 0):
        # if we went over the specified angle, reverses the direction and
        # decreases the angular speed to have a better chance of sampling
        # at the right moment.
            curr_angular_velocity*=0.8
            direction=-direction

        set_angular_velocity(curr_angular_velocity*(-direction))
    stop()
