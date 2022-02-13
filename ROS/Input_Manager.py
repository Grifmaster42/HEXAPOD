#!/usr/bin/env python3
# 

import math
import roslibpy as rospy
import time
import transfer.msg


class InputManager:

    def __init__(self):
        self.speed = 0.0
        self.angle = 0.0
        self.button = 0
        rospy.init_node('listener', anonymous=True)
        rospy.Subscriber('ControllerInput', transfer, self.callback)
        self.dataPackage = [0.0, 0.0, 0]

    def callback(self, data: transfer):
        self.angle = round(data.angle, 2)
        self.speed = round(data.speed, 2)
        self.button = data.button
        self.dataPackage = [self.angle, self.speed, self.button]
        rospy.loginfo('DataPackage: ' + str(self.dataPackage))

    def getData(self):
        return self.dataPackage


if __name__ == '__main__':
    iM = InputManager()
    while True:
        rospy.loginfo(iM.getData())
        time.sleep(0.5)
