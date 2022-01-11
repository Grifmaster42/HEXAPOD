import time
import zmq
import msgpack
import random


# Test 123

class HexaplotSender:

    def __init__(self, ip="127.0.0.2", port=5555):
        context = zmq.Context()

        self.socket = context.socket(zmq.PAIR)
        self.socket.connect("tcp://" + ip + ":" + str(port))
        self.traj = [[-1, 0, 0], [-0.5, 0, 0.75], [0, 0, 1], [0.5, 0, 0.75], [1, 0, 0], [0.5, 0, 0], [0, 0, 0],
                     [-0.5, 0, 0], [-1, 0, 0]]

    def send_points(self, lines=None):
        data = lines
        self.socket.send(msgpack.packb(data))

    def walk(self, fac=0.05, sleep=0.5):
        dummyPoints = [
            (-0.05, 0.1, 0.0),
            (-0.1, 0.0, 0.0),
            (-0.05, -0.1, 0.0),
            (0.05, -0.1, 0.0),
            (0.1, 0.0, 0.0),
            (0.05, 0.1, 0.0)]

        while True:
            newPoints = []
            for i, points in enumerate(dummyPoints):
                x = points[0] + random.random() * fac
                y = points[1] + random.random() * fac
                z = points[2] + random.random() * fac
                newPoints.append((x, y, z))
            self.send_points([newPoints,newPoints])
            time.sleep(sleep)

    def setNewTraj(self, traj):
        self.traj.clear()
        self.traj = traj

    def trayLine(self, traj=None, coord=(0, 0, 0), length=1, height=1):
        if traj is None:
            traj = self.traj

        return [[traj[0][0] * length + coord[0], traj[0][1] + coord[1], traj[0][2] + coord[2]],
                # 1                    height
                [traj[1][0] * length + coord[0], traj[1][1] + coord[1], traj[1][2] * height + coord[2]],
                # 2                      3
                [traj[2][0] + coord[0], traj[2][1] + coord[1], traj[2][2] * height + coord[2]],
                # 3                      |
                [traj[3][0] * length + coord[0], traj[3][1] + coord[1], traj[3][2] * height + coord[2]],
                # 4                      |
                [traj[4][0] * length + coord[0], traj[4][1] + coord[1], traj[4][2] + coord[2]],
                # 5              2       |       4
                [traj[5][0] * length + coord[0], traj[5][1] + coord[1], traj[5][2] + coord[2]],
                # 6                      |
                [traj[6][0] + coord[0], traj[6][1] + coord[1], traj[6][2] + coord[2]],  # 7                      |
                [traj[7][0] * length + coord[0], traj[7][1] + coord[1], traj[7][2] + coord[2]],
                # 8     1/9      8       7       6       5
                [traj[8][0] * length + coord[0], traj[8][1] + coord[1],
                 traj[8][2] + coord[2]]]  # 9   -1 ------------------------------------> 1 length

    def givepoints(self, points, sleep=0.1):
        self.send_points(points)
        time.sleep(sleep)

    def leg(self, sleep=0.5, dummyPoints=None):
        dummyPoints = self.trayLine(coord=(3, 1.5, 0), length=1.5)

        while True:
            for points in dummyPoints[0:-1]:
                self.send_points(
                    [points, (points[0], points[1] + 7, points[2]), (points[0] + 6, points[1] + 3.5, points[2])])
                time.sleep(sleep)

    def random_dot(self, step_size=0.1, sleep=0.1):
        while True:
            for elem in self.traj:
                self.send_points(elem)
                time.sleep(sleep)


if __name__ == "__main__":
    hps = HexaplotSender()

    # hps.random_dot(sleep=0.5)
    # hps.leg()
    hps.walk()
