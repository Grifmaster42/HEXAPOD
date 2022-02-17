import time

from PyQt5.QtCore import *

__name__ = "worker"


class Worker(QThread):
    # Signale erzeugen
    set_slider_pos_sig = pyqtSignal(float, float, float)
    do_communication_sig = pyqtSignal()
    set_control_to_controller_sig = pyqtSignal()
    set_control_to_gui_sig = pyqtSignal()
    set_mode_normal_sig = pyqtSignal()
    set_mode_parkour_sig = pyqtSignal()
    set_mode_fast_sig = pyqtSignal()
    finished_sig = pyqtSignal()

    # Variablen
    time_sleep = 0.05

    def __init__(self, control):
        super(Worker, self).__init__()
        # Controllerobjekt übergeben bekommen
        self.control = control
        self.on = False
        self.control_by_controller = False
        if self.control.get_controller() is not None:
            self.on = True
            self.control_by_controller = True

    def run(self):
        while True:
            self.work()

    def work(self):
        while self.on:
            # Prüfen ob über GUI oder Controller gesteuert werden soll
            if self.control.is_up():
                self.set_control_to_controller_sig.emit()
                self.control_by_controller = True
            if self.control.is_down():
                self.set_control_to_gui_sig.emit()
                self.control_by_controller = False
            # Controller abfragen, falls Controllersteuerung aktiv
            if self.control_by_controller:
                # Stick abfragen und Werte an GUI senden
                self.set_slider_pos_sig.emit(self.control.get_lx(), self.control.get_ly(), self.control.get_rt())
                # Buttons abfragen und an GUI senden
                if self.control.is_y():
                    self.set_mode_normal_sig.emit()
                if self.control.is_b():
                    self.set_mode_parkour_sig.emit()
                if self.control.is_a():
                    self.set_mode_fast_sig.emit()
            # Signal zum senden der Daten schicken
            self.do_communication_sig.emit()
            time.sleep(self.time_sleep)

    def controller_reconnect(self):
        if self.control.init_controller():
            self.start_work()

    def stop_work(self):
        self.on = False

    def start_work(self):
        if self.control.get_controller is None:
            self.control_by_controller = False
            self.set_control_to_gui_sig.emit()
        self.on = True

    def set_controller_control(self, controller_control_bool):
        self.control_by_controller = controller_control_bool
