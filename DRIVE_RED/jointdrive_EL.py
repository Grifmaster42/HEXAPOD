import math
from DRIVE_RED.servo_ax12a_EL import *

import time


# Class definition of ax12a-controller class, defines interface to the robot
# ===============================================================================
# Implements the interface between leg- and servo class
# ------------------------------------------------------------------------------
# Provides all required methods that allow the leg class to control the servo
# Implements all nessesary codomain conversion between leg- and servo values
# Limits values too valid servo values
# Servo uses ticks from 0 to 1023 for angle and speed
# Leg uses angles in radian and rotation per minit for speed
# Defines zero angle as average of min- and max value -> positive and negativ angles are allowed
class JointDrive(ServoAx12a):
    # Definition of public class attributes
    # ----------------------------------------------------------------------
    _ANGLE_RADIAN_ZERO = (ServoAx12a._ANGLE_MAX_DEGREE
                          - ServoAx12a._ANGLE_MIN_DEGREE) * math.pi / 360  # Zero angle offset of servo in radian
    _ANGLE_RADIAN_MAX = ServoAx12a._ANGLE_MAX_DEGREE * 2 * math.pi / 360  # Max angle offset of servo in radian
    _ANGLE_RADIAN_MIN = ServoAx12a._ANGLE_MIN_DEGREE * 2 * math.pi / 360  # Min angle offset of servo in radian
    _ANGLE_UNIT = ServoAx12a._ANGLE_MAX_TICKS / \
                  ((ServoAx12a._ANGLE_MAX_DEGREE - ServoAx12a._ANGLE_MIN_DEGREE) * math.pi * 2 / 360)  # Ticks per rad

    _CONST_ANGLE_TO_TICKS = ServoAx12a._SPEED_MAX_TICKS / (5 * math.pi / 3)    #5,235
    _CONST_SPEED_TO_TICKS = ServoAx12a._SPEED_MAX_TICKS / ServoAx12a._SPEED_MAX_RPM

    _CONST_CIRCLE_RADIAN = math.pi * 2

    # Private methods
    # ----------------------------------------------------------------------
    # Constructor, defines the folowing variables: counterClockWise, angleOffset, angleMax, angleMin
    # id -> id of servo, cw -> rotating direction, aOffset -> angle offset,
    # aMax -> maximum angle allowed, aMin -> minimum angle allowed
    def __init__(self, id, ccw=False, aOffset=0.0, aMax=math.pi, aMin= -(math.pi)):
        self.id = id
        self.counterClockWise = ccw
        """        
        self.angleMax = aMax if (
                aMin < aMax <= self._ANGLE_RADIAN_MAX and aMax >= self._ANGLE_RADIAN_MIN) else self._ANGLE_RADIAN_MAX
        self.angleMin = aMin if (
                aMax > aMin >= self._ANGLE_RADIAN_MIN and aMin <= self._ANGLE_RADIAN_MAX) else self._ANGLE_RADIAN_MIN
        """
        self.angleMax = + JointDrive._ANGLE_RADIAN_ZERO
        self.angleMin = - JointDrive._ANGLE_RADIAN_ZERO
        if aMax < aMin or aMax > self.angleMax:
            aMax = self.angleMax
        self.angleMax = aMax
        if aMin > aMax or aMin < self.angleMin:
            aMin = self.angleMin
        self.angleMin = aMin
        self.angleOffset = aOffset
        self.curAngle = 0
        super().__init__(id)


    # Converts angle in radian to servo ticks
    # angle -> in radian, returns angle in servo ticks
    def __convertAngleToTicks(self, angle):
        if angle < self.angleMin:
            angle = self.angleMin

        if angle > self.angleMax:
            angle = self.angleMax
        if self.counterClockWise:
            angle = self._ANGLE_RADIAN_ZERO + self.angleOffset + angle

        else:
            angle = self._ANGLE_RADIAN_ZERO - self.angleOffset - angle
        return int((abs(self._CONST_ANGLE_TO_TICKS * angle)))    # Converts servo ticks to angle in radian


    # ticks -> servo ticks, returns angle in radian
    def __convertTicksToAngle(self, ticks):
        #print("Ticks:", ticks)
        angle = ticks / self._ANGLE_UNIT
        #print("Winkelll ", math.degrees(angle))
        if self.counterClockWise:
            angle -= (self._ANGLE_RADIAN_ZERO + self.angleOffset)   # 150+0         !!!!!!!!!!!!offset!!! beachten, wenn ein Wert für eingesetzt wird
            #print("If Fall")
        else:
            angle += (self._ANGLE_RADIAN_ZERO + self.angleOffset)   #150+0
            #print("Else Fall")
        #print("winkel: " , math.degrees(angle))
        return angle


    # Converts speed in rpm to servo ticks
    # speed -> value in rpm
    def __convertSpeedToTicks(self, speed):
        ticks = speed / self._SPEED_UNIT
        return int(ticks)


    # Converts ticks to speed in rpm
    # ticks -> servo ticks
    def __convertTicksToSpeed(self, ticks):
        speed = ticks * self._SPEED_UNIT
        return speed


    # Public methods
    # ----------------------------------------------------------------------
    # Get current angle of servo
    # returns angle in radian
    def getCurrentJointAngle(self):
        self.curAngle = self.__convertTicksToAngle(self.getPresentPosition())
        return self.curAngle


    # Set servo to desired angle
    # angle -> in radian,
    # speed -> speed of movement, speed < 0 -> no speed set, speed = 0 -> maximum speed
    def setDesiredJointAngle(self, angle, trigger=False):
        success = self.setGoalPosition(self.__convertAngleToTicks(angle), trigger)
        if success:
            self.curAngle = angle
        return success


    # Set servo to desired angle
    # angle -> in radian,
    # speed -> speed of movement in rpm, speed = 0 -> maximum speed
    def setDesiredAngleSpeed(self, angle, speed=0, trigger=False):
        # convert angle to positive if needed

        speed_in_ticks = self.__convertSpeedToTicks(speed)
        angle_in_ticks = self.__convertAngleToTicks(angle)

        success = self.setGoalPosSpeed(angle_in_ticks, speed_in_ticks, trigger)

        if success:
            self.curAngle = self.curAngle - angle

        return success


    # Set speed value of servo
    # speed -> angle speed in rpm
    def setSpeedValue(self, speed, trigger=False):
        speed_in_ticks = self.__convertSpeedToTicks(speed)
        speedValue = self.setMovingSpeed(speed_in_ticks, trigger)
        return speedValue

    def broadcast(self):
        self.action()

# Broadcast = 19 ServoMotor, ID:254