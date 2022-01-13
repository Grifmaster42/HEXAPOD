class Leg:
    gotPoint = False
    def __init__(self,lange,offset,rotation,a,b,kp):
        self.offset = kp
        self.x = offset[0]
        self.y = offset[1]
        self.z = 0
        if rotation == 0:
            self.x = self.x + lange[0] + lange[2] + lange[3] + lange[5]
            self.y = self.y
        elif rotation == 1:
            self.x = self.x
            self.y = offset[1] - lange[0] - lange[2] - lange[3] - lange[5]
        elif rotation == 2:
            self.x = self.x - lange[0] - lange[2] - lange[3] - lange[5]
            self.y = offset[1]
        elif rotation == 3:
            self.x = self.x
            self.y = offset[1] + lange[0] + lange[2] + lange[3] + lange[5]
        self.nextPoint = [self.x,self.y,self.z]
        self.z2 = kp[2]

    def setPosition(self,coord):
        self.nextPoint = coord[0:-1]

    def getOffset(self):
        return self.offset+[1]

    def getOffsetFoot(self):
        return self.x, self.y, self.z
    
    def getPosition(self):
        return self.nextPoint+[1]

    @staticmethod
    def convert(pos, add=False):
        if add:
            return [pos[0], pos[1], pos[2], 1]
        else:
            return pos[:-1]
        