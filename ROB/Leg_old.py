class Leg:
    gotPoint = False
    def __init__(self,lange,offset,rotation):
        self.offset = offset
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
        self.z2 = 0.151

    def setPosition(self,coord):
        self.nextPoint = [self.x + coord[0],self.y + coord[1],self.z + coord[2]]

    def get_offset_leg(self):
        return self.offset[0], self.offset[1], self.z2

    def get_offset_foot(self):
        return self.x, self.y, self.z
    
    def getPosition(self):
        return self.nextPoint
        