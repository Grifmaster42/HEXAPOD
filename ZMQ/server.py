import zmq
from threading import Thread
import msgpack

__name__ = "server"


class Server():

    __PORT = "6969"

    def __init__(self):
        self.data = 0

        # ZMQ Context erstellen, Socket erstellen
        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self.socket.bind("tcp://*:"+self.__PORT)

        # Thread zum empfangen der Daten erstellen und starten
        listen_thread = Thread(target=self.listen, args=(self.socket,))
        listen_thread.start()

    def listen(self, socket):
        # Nach vom Client gesendeten Daten fragen und ggf. speichern
        while True:
            try:
                self.data = msgpack.unpackb(socket.recv())
            except zmq.ZMQError as error:
                # print("Ein Fehler ist aufgetreten!\nError 404: \"Error not found!\"")
                print("Receiven fehlgeschlagen: " + error)

    def get_data(self):
        # Daten zurückgeben
        return self.data

    def send_data(self, data):
        # Daten an Server senden
        try:
            self.socket.send(msgpack.packb(data))
        except zmq.ZMQError as error:
            print("Senden fehlgeschlagen: " + error)
