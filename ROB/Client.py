import math
import time

import zmq
from threading import Thread
import msgpack
import ROB.HexaplotSender as Hxps
# import time
# import controller

class Steuerung:

    __PORT = "6969"

    def __init__(self):
        self.sender = Hxps.HexaplotSender()
        self.data = 0

        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self.socket.connect("tcp://127.0.0.1:"+self.__PORT)

        listen_thread = Thread(target=self.listen, args=(self.socket,))
        listen_thread.start()

    def listen(self, socket):
        while True:
            try:
                self.data = msgpack.unpackb(socket.recv())
            except any:
                print(any)
                pass

    def getData(self):
        return self.data

    def sendData(self, data):
        self.socket.send(msgpack.packb(data))

def main():
    st = Steuerung()
    an = True
    while an:
        #x = float(input("X: "))
        #y = float(input("Y: "))
        #gangart = input("Gangart: ")
        data = [1,- math.pi/1.5, "Dreieck"]
        st.send_data(data)
        time.sleep(1)

if __name__ == '__main__':
    main()