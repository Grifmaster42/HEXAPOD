import numpy as np
# from DRIVE.jointdrive_edit import *
import math

class Leg:

    # a -> Laengenmaße (in m)
    # b -> Offset [x_B, y_B] (in m)
    # r -> Rotationswinkel (in rad)
    # m -> Motorobjekte
    # n -> Nullwinkel der Motoren
    def __init__(self, a=[1, 1, 1, 1, 1, 1, 1], b=[0, 0], r=0, m=[0, 0, 0], n=[0, 0, 0], offset_f=[0, 0, 0]):
        self.a = [a[0], a[1], a[2], a[3], a[4], a[5], a[6]]
        self.offset = [b[0], b[1]]
        self.rotation = r
        self.offset_f = offset_f

        self.lc = self.a[2]
        self.lcSquare = math.pow(self.lc, 2)
        self.lf = math.sqrt(math.pow(self.a[3], 2) + math.pow(self.a[4], 2))
        self.lfSquare = math.pow(self.lf, 2)
        self.lt = math.sqrt(math.pow(self.a[5], 2) + math.pow(self.a[6], 2))
        self.ltSquare = math.pow(self.lt, 2)
        self.servoOffset = [math.cos(self.rotation) * self.a[0], math.sin(self.rotation) * self.a[0], -self.a[1], 0]

        # für Geschwindigkeitsberechnung (wird nicht verwendet)
        self.lastPosition = [0, 0, 0]

        self.turnOffset = [n[0], n[1], n[2]]
        self.goalAngle = [0,0,0]
        #servoA = JointDrive(m[0], aOffset=self.turnOffset[0], ccw=False, prt=True, aMax=math.radians(120), aMin=math.radians(-120))
        #servoB = JointDrive(m[1], aOffset=self.turnOffset[1], ccw=True, prt=True, aMax=math.radians(120), aMin=math.radians(-120))
        #servoC = JointDrive(m[2], aOffset=self.turnOffset[2], ccw=False, prt=True, aMax=math.radians(120),  aMin=math.radians(-120))
        #self.motors = [servoA, servoB, servoC]

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
        H = np.array([
            [math.cos(-self.rotation), -math.sin(-self.rotation), 0, -self.offset[0]],
            [math.sin(-self.rotation), math.cos(-self.rotation), 0, -self.offset[1]],
            [0, 0, 1, 0],
            [0, 0, 0, 1]])
        pos = np.dot(H, noServoOffset)
        return pos

    # Methoden für die ROB Gruppe

    # Gibt die Offset Fußposition im Base-KS an
    def getOffset(self):
        return self.offset_f + [1]

    # Gibt die Fussposition im Base-KS an
    def getPosition(self):
        H = np.array([
            [math.cos(self.rotation), -math.sin(self.rotation), 0, self.offset[0]],
            [math.sin(self.rotation), math.cos(self.rotation), 0, self.offset[1]],
            [0, 0, 1, 0],
            [0, 0, 0, 1]])
        Hp = np.dot(H, self.forKinAlphaJoint(self.goalAngle[0], self.goalAngle[1], self.goalAngle[2]))
        posnp = np.add(Hp, self.servoOffset)
        return posnp.tolist()

    # Setzt die Fussspitze auf die gegebene Position aus dem Base-KS
    def setPosition(self, pos=[0, 0, 0, 1]):
        goalAngle = self.invKinAlphaJoint(self.baseCStoLegCS(pos))
        self.goalAngle = goalAngle
        # self.motors[0].setDesiredJointAngle([goalAngle[0]])
        # self.motors[1].setDesiredJointAngle([goalAngle[1]])
        # self.motors[2].setDesiredJointAngle([goalAngle[2]])
        return goalAngle

    # Gibt die Gelenkposition im Base-KS an. In pos werden die Plotter-Methoden unten verwendet (z.B. getPosAlpha())
    def getJointPosition(self, ai=[0, 0, 0, 1]):
        pos = ai[:, -1]
        H = np.array([
            [math.cos(self.rotation), -math.sin(self.rotation), 0, self.offset[0]],
            [math.sin(self.rotation), math.cos(self.rotation), 0, self.offset[1]],
            [0, 0, 1, 0],
            [0, 0, 0, 1]])
        Hp = np.dot(H, pos)
        posnp = np.add(Hp, self.servoOffset)
        pos = [posnp[0], posnp[1], posnp[2], 1]
        return pos

    # Gibt die aktuellen(!!!) Winkel der Gelenke an
    # def getMotorAngles(self):
    #    return [self.motors[0].getCurrentJointAngle(), self.motors[1].getCurrentJointAngle(),
    #            self.motors[2].getCurrentJointAngle()]

    @staticmethod
    def convert(pos, add=False):
        if add:
            return [pos[0], pos[1], pos[2], 1]
        else:
            return pos[:-1]

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
