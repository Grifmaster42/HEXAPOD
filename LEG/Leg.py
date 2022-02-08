import time

import numpy as np
from DRIVE.jointdrive_edit import *
import ROB.config as cn


class Leg:

    # a -> Laengenmaße (in m)
    # b -> Offset [x_B, y_B] (in m)
    # r -> Rotationswinkel (in rad)
    # m -> Motorobjekte
    # n -> Nullwinkel der Motoren
    def __init__(self, a=[1, 1, 1, 1, 1, 1, 1], b=[0, 0], r=0, m=[0, 0, 0], n=[0, 0, 0], start=[0, 0, 0],
                 ccw=[True, True, True]):

        self.scaled_speed = cn.robot['test']

        self.old_angle = [0,0,0]

        print("erreivht")
        self.a = [a[0], a[1], a[2], a[3], a[4], a[5], a[6]]
        self.offset = [b[0], b[1]]
        self.rotation = r
        self.start = start

        self.goalAngle = [n[0], n[1], n[2]]

        self.lc = self.a[2]
        self.lcSquare = math.pow(self.lc, 2)
        self.lf = math.sqrt(math.pow(self.a[3], 2) + math.pow(self.a[4], 2))
        self.lfSquare = math.pow(self.lf, 2)
        self.lt = math.sqrt(math.pow(self.a[5], 2) + math.pow(self.a[6], 2))
        self.ltSquare = math.pow(self.lt, 2)
        self.servoOffset = [math.cos(self.rotation) * self.a[0], math.sin(self.rotation) * self.a[0], -self.a[1], 0]

        # für Geschwindigkeitsberechnung (wird nicht verwendet)
        self.lastPosition = [0, 0, 0]

        # self.turnOffset = [n[0], n[1], n[2]]
        beta_offset = math.atan2(self.a[4], self.a[3])
        gamma_offset = math.pi / 2 - math.atan2(self.a[5], self.a[6]) - beta_offset

        servoA = JointDrive(m[0], aOffset=0, ccw=ccw[0], aMax=math.radians(120), aMin=math.radians(-120))
        servoB = JointDrive(m[1], aOffset=beta_offset, ccw=ccw[1], aMax=math.radians(110), aMin=math.radians(-110))
        servoC = JointDrive(m[2], aOffset=gamma_offset, ccw=ccw[2], aMax=math.radians(110), aMin=math.radians(-110))

        self.motors = [servoA, servoB, servoC]

        for motor in self.motors:
            motor.setSpeedValue([10])

        #self.motors[0].setDesiredJointAngle([0])
        #self.motors[1].setDesiredJointAngle([0])
        #self.motors[2].setDesiredJointAngle([0])
        #time.sleep(0.02)

    # Vorgegebene Methoden
    def forKinAlphaJoint(self, alpha, beta, gamma):
        pos = [0, 0, 0, 1]
        pos[0] = math.cos(alpha) * (self.lt * math.cos(beta + gamma) + self.lf * math.cos(beta) + self.lc)
        pos[1] = math.sin(alpha) * (self.lt * math.cos(beta + gamma) + self.lf * math.cos(beta) + self.lc)
        pos[2] = self.lt * math.sin(beta + gamma) + self.lf * math.sin(beta)
        return pos

    def invKinAlphaJoint(self, pos=[0, 0, 0, 1]):
        alpha = math.atan2(pos[1], pos[0])
        footPos = np.array(pos)
        A1 = np.array([
            [math.cos(alpha), 0, math.sin(alpha), self.lc * math.cos(alpha)],
            [math.sin(alpha), 0, -math.cos(alpha), self.lc * math.sin(alpha)],
            [0, 1, 0, 0],
            [0, 0, 0, 1]])
        betaPos = np.dot(A1, np.transpose([0, 0, 0, 1]))
        lct = np.linalg.norm(footPos[0:3] - betaPos[0:3])
        lctSquare = math.pow(lct, 2)
        gamma = math.acos((self.ltSquare + self.lfSquare - lctSquare) / (2 * self.lt * self.lf)) - math.pi
        h1 = math.acos((self.lfSquare + lctSquare - self.ltSquare) / (2 * self.lf * lct))
        h2 = math.acos((lctSquare + self.lcSquare - math.pow(np.linalg.norm(footPos[0:3]), 2)) / (2 * self.lc * lct))
        if footPos[2] < 0:
            beta = (h1 + h2) - math.pi
        else:
            beta = (math.pi - h2) + h1
        return [alpha, beta, gamma]

    # Hilfsmethoden
    def baseCStoLegCS(self, pos=[0, 0, 0, 1]):
        noServoOffset = np.subtract(pos, self.servoOffset)
        noServoOffset = np.subtract(noServoOffset, self.offset + [0, 0])
        H = np.array([
            [math.cos(-self.rotation), -math.sin(-self.rotation), 0, 0],
            [math.sin(-self.rotation), math.cos(-self.rotation), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]])
        # H = np.array([
        #     [math.cos(-self.rotation), -math.sin(-self.rotation), 0, -self.offset[0]],
        #     [math.sin(-self.rotation), math.cos(-self.rotation), 0,  -self.offset[1]],
        #     [0, 0, 1, 0],
        #     [0, 0, 0, 1]])
        pos = np.dot(H, np.transpose(noServoOffset))
        return pos

    # Methoden für die ROB Gruppe

    # Gibt die Offset Fußposition im Base-KS an
    def getOffset(self):
        return self.start

    # Gibt die Fussposition im Base-KS an
    def getPosition(self):
        H = np.array([
            [math.cos(self.rotation), -math.sin(self.rotation), 0, self.offset[0]],
            [math.sin(self.rotation), math.cos(self.rotation), 0, self.offset[1]],
            [0, 0, 1, 0],
            [0, 0, 0, 1]])
        Hp = np.dot(H, self.forKinAlphaJoint(self.goalAngle[0], self.goalAngle[1], self.goalAngle[2]))
        # Hp = np.dot(H, self.forKinAlphaJoint(self.motors[0].getCurrentJointAngle(), self.motors[1].getCurrentJointAngle(), self.motors[2].getCurrentJointAngle()))
        posnp = np.add(Hp, self.servoOffset)
        pos = [posnp[0], posnp[1], posnp[2], 1]
        return pos

    # Setzt die Fussspitze auf die gegebene Position aus dem Base-KS
    def setPosition(self, pos=[0, 0, 0, 1], speed = 10):
        self.goalAngle = self.invKinAlphaJoint(self.baseCStoLegCS(pos))
        self.diff_angle = [0,0,0]
        for i in range(3):
            self.diff_angle[i] = abs(self.goalAngle[i] - self.old_angle[i])
        max_val = max(self.diff_angle)
        for i in range(3):
            if self.scaled_speed:
                self.motors[i].setGoalPosSpeed([self.goalAngle[i],speed/max_val*self.diff_angle[i]], trigger= True)
            else:
                self.motors[i].setGoalPosSpeed([self.goalAngle[i], speed], trigger=True)
        # self.motors[1].setGoalPosSpeed([self.goalAngle[1], speed], trigger=True)
        # self.motors[2].setGoalPosSpeed([self.goalAngle[2], speed], trigger=True)
        return self.goalAngle

    # Gibt die Gelenkposition im Base-KS an. Mit point wird die Gelenkposition gewaehlt
    def getJointPosition(self, point):
        if point == 0:
            pos = [0, 0, 0, 1]
        elif point == 1:
            pos = self.getPosAlpha()[:, -1]
        elif point == 2:
            pos = self.getPosBeta()[:, -1]
        elif point == 3:
            pos = self.getPosGamma()[:, -1]
        else:
            pos = self.getPosFoot()[:, -1]
        H = np.array([
            [math.cos(self.rotation), -math.sin(self.rotation), 0, self.offset[0]],
            [math.sin(self.rotation), math.cos(self.rotation), 0, self.offset[1]],
            [0, 0, 1, 0],
            [0, 0, 0, 1]])
        Hp = np.dot(H, pos)
        # return np.add(Hp, self.servoOffset)
        return Hp.tolist()

    # Gibt die aktuellen(!!!) Winkel der Gelenke an
    def getMotorAngles(self):
        return [self.goalAngle[0],
                self.goalAngle[1],
                self.goalAngle[2]]


    # Zu Testzwecken im Plotter
    def getPosCreateAi(self, a, alpha, d, theta):
        return np.array([
            [math.cos(theta), -math.sin(theta) * math.cos(alpha), math.sin(theta) * math.sin(alpha),
             a * math.cos(theta)],
            [math.sin(theta), math.cos(theta) * math.cos(alpha), -math.cos(theta) * math.sin(alpha),
             a * math.sin(theta)],
            [0, math.sin(alpha), math.cos(alpha), d],
            [0, 0, 0, 1]])

    def getPosAlpha(self):
        A0 = self.getPosCreateAi(self.a[0], 0, -self.a[1], 0)
        return A0

    def getPosBeta(self):
        A1 = self.getPosCreateAi(self.lc, math.pi / 2, 0, self.goalAngle[0])
        return np.dot(self.getPosAlpha(), A1)

    def getPosGamma(self):
        A2 = self.getPosCreateAi(self.lf, 0, 0, self.goalAngle[1])
        return np.dot(self.getPosBeta(), A2)

    def getPosFoot(self):
        A3 = self.getPosCreateAi(self.lt, 0, 0, self.goalAngle[2])
        return np.dot(self.getPosGamma(), A3)
