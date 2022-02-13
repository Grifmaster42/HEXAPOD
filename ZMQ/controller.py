from threading import Thread

import pygame

__name__ = "controller"


class Controller:
    # Listen mit Daten des Controllerzustandes
    axes_data = {}
    button_data = {}
    d_pad_data = (0, 0)  # ( Right=1/Left=-1, Up=1/Down=-1 )

    # Weitere Variablen
    round_figure = 2
    schwellwert_axis = 0.1
    schwellwert_trigger = 0.2

    #                           Defaultwerte ( in gettern überarbeitet )
    LX = 0  # Stick Links X ( Links negativ, rechts positiv )
    LY = 1  # Stick Links Y ( oben negativ, unten positiv ) -> ( ... * -1 ) -> oben positiv
    RX = 2  # Stick Rechts X ( Links negativ, rechts positiv )
    RY = 3  # Stick Rechts Y ( oben negativ, unten positiv ) -> ( ... * -1 ) -> oben positiv
    LT = 4  # Trigger Links ( default -1, halb drücken 0, ganz drücken 1 ) -> ((... + 1 ) / 2) -> von 0 bis 1
    RT = 5  # Trigger Rechts ( default -1, halb drücken 0, ganz drücken 1 ) -> ((... + 1 ) / 2) -> von 0 bis 1
    A = 0  # A Button
    B = 1  # B Button
    X = 2  # X Button
    Y = 3  # Y Button
    LB = 4  # Links Bumper
    RB = 5  # Rechts Bumper
    BB = 6  # Back Button ( Links )
    SB = 7  # Start Button ( Rechts )
    LI = 8  # Stick Links In
    RI = 9  # Stick Rechts In
    GB = 10  # Guide Button ( geht nicht )

    def __init__(self):
        # Controller erstellen, wenn möglich
        pygame.init()
        pygame.joystick.init()
        self.on = False
        try:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()

            # Listen zum ersten mal befüllen
            for i in range(self.controller.get_numaxes()):
                self.axes_data[i] = 0
            self.axes_data[self.LT] = -1
            self.axes_data[self.RT] = -1

            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

            self.on = True
        except BaseException as error:
            print(error)
            self.controller = None

        # Thread zum auslesen der Controllerevents erstellen und starten
        self.listen_thread = Thread(target=self.listen, args=())
        self.listen_thread.start()

    def get_controller(self):
        return self.controller

    def init_controller(self):
        try:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()

            # Listen zum ersten mal befüllen
            for i in range(self.controller.get_numaxes()):
                self.axes_data[i] = 0
            self.axes_data[self.LT] = -1
            self.axes_data[self.RT] = -1

            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

            self.start_thread()
        except BaseException as error:
            print(error)
            self.controller = None
            return False
        return True

    def start_thread(self):
        self.on = True

    def stop_thread(self):
        self.on = False

    def listen(self):

        # print(self.controller.get_name())
        while True:
            # durchgehend Events vom Controller empfangen und speichern
            while self.on:
                for event in pygame.event.get():
                    # Stick und Trigger
                    if event.type == pygame.JOYAXISMOTION:
                        self.axes_data[event.axis] = round(event.value, self.round_figure)
                    # Button drücken
                    elif event.type == pygame.JOYBUTTONDOWN:
                        self.button_data[event.button] = True
                    # Button wieder loslassen
                    elif event.type == pygame.JOYBUTTONUP:
                        self.button_data[event.button] = False
                    # Directionpad
                    elif event.type == pygame.JOYHATMOTION:
                        self.d_pad_data = event.value

    # Getter mit teilweise überarbeitung der Werte des Controllers um mit den Werten arbeiten zu können
    def get_lx(self):
        if abs(self.axes_data[self.LX]) <= self.schwellwert_axis:
            return 0
        return self.axes_data[self.LX]

    def get_ly(self):
        if abs(self.axes_data[self.LY]) <= self.schwellwert_axis:
            return 0
        return self.axes_data[self.LY] * -1

    def get_rx(self):
        if abs(self.axes_data[self.RX]) <= self.schwellwert_axis:
            return 0
        return self.axes_data[self.RX]

    def get_ry(self):
        if abs(self.axes_data[self.RY]) <= self.schwellwert_axis:
            return 0
        return self.axes_data[self.RY] * -1

    def get_lt(self):
        if 1 + self.axes_data[self.LT] < self.schwellwert_trigger:
            return 0
        return round((self.axes_data[self.LT] + 1) / 2, self.round_figure)

    def get_rt(self):
        if 1 + self.axes_data[self.RT] < self.schwellwert_trigger:
            return 0
        return round((self.axes_data[self.RT] + 1) / 2, self.round_figure)

    def is_up(self):
        if self.d_pad_data[1] == 1:
            return True
        else:
            return False

    def is_down(self):
        if self.d_pad_data[1] == -1:
            return True
        else:
            return False

    def is_left(self):
        if self.d_pad_data[0] == -1:
            return True
        else:
            return False

    def is_right(self):
        if self.d_pad_data[0] == 1:
            return True
        else:
            return False

    def is_a(self):
        return self.button_data[self.A]

    def is_b(self):
        return self.button_data[self.B]

    def is_x(self):
        return self.button_data[self.X]

    def is_y(self):
        return self.button_data[self.Y]

    def is_lb(self):
        return self.button_data[self.LB]

    def is_rb(self):
        return self.button_data[self.RB]

    def is_bb(self):
        return self.button_data[self.BB]

    def is_sb(self):
        return self.button_data[self.SB]

    def is_sli(self):
        return self.button_data[self.LI]

    def is_sri(self):
        return self.button_data[self.RI]

    def is_gb(self):
        return self.button_data[self.GB]
