import time
import math
from DRIVE.jointdrive_edit import *

id = 4
mid_pos = [0]
max_pos = [(5/6)*math.pi]
min_pos = [-(5/6)*math.pi]
speed20 = [20]
speed60 = [60]


servo = JointDrive(4, ccw=True, prt=False, aMax=math.radians(120), aMin=math.radians(-120))
servo1 = JointDrive(10, ccw=False, prt=False, aMax=math.radians(120), aMin=math.radians(-120))
servo2 = JointDrive(15, ccw=True, prt=False, aMax=math.radians(120), aMin=math.radians(-120))
servo3 = JointDrive(17, ccw=False, prt=False, aMax=math.radians(120), aMin=math.radians(-120))




servo.setDesiredJointAngle([math.radians(0)], trigger=True)



x = -150
for i in range(1, 114, 10):
    x *= -1
    servo.setGoalPosSpeed([math.radians(x), i], trigger=True)
    servo1.setGoalPosSpeed([math.radians(x), i], trigger=True)
    servo2.setGoalPosSpeed([math.radians(x), i], trigger=True)
    servo3.setGoalPosSpeed([math.radians(x), i], trigger=True)

    time.sleep(1)

    servo.action()
    y = str(servo.getSpeedValue())
    time.sleep(1)
    print(y)
    time.sleep(1)
    print(servo.getPresentTemperature())
