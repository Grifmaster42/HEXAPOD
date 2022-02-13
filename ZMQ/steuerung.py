import zmq
import msgpack
from threading import Thread



__name__ = "steuerung"


class Steuerung():

    __PORT = "6969"

    def __init__(self):
        self.data = 0

        # ZMQ Context erstellen, Socket erstellen und mit Server verbinden
        context = zmq.Context()
        self.socket = context.socket(zmq.PAIR)
        self.socket.connect("tcp://10.134.31.4:" + self.__PORT)
        #self.socket.connect("tcp://127.0.0.1:"+self.__PORT)

        # Thread zum empfangen der Daten erstellen und starten
        listen_thread = Thread(target=self.listen, args=(self.socket,))
        listen_thread.start()
        # music_thread = Thread(target=self.music, args=())
        # music_thread.start()

    def listen(self, socket):
        # Nach vom Server gesendeten Daten fragen und ggf. speichern
        while True:
            try:
                self.data = msgpack.unpackb(socket.recv())
            except zmq.ZMQError as error:
                #print("Ein Fehler ist aufgetreten!\nError 404: \"Error not found!\"")
                print("Receiven fehlgeschlagen: " + error)

    # def music(self):
    #     pygame.mixer.init()
    #     pygame.mixer.music.load(musiclink)
    #     pygame.mixer.music.play()
    #     while pygame.mixer.music.get_busy() == True:
    #         continue

    def get_data(self):
        # Daten zurückgeben
        return self.data

    def send_data(self, data):
        # Daten an Server senden
        try:
            self.socket.send(msgpack.packb(data))
        except zmq.ZMQError as error:
            print("Senden fehlgeschlagen: " + error)
