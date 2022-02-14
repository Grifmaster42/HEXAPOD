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


if __name__ == "__main__":
    hps = HexaplotSender()

    hps.walk()
