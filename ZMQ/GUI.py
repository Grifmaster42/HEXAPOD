import sys
import controller
import steuerung
import worker
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import *
import math

__name__ = '__main__'

# Variablen
music_link = "RESSOURCES/fafboi.mp3"
bg_normal = "RESSOURCES/background_blue.jpg"
bg_parkour = "RESSOURCES/background.jpg"
bg_parkour_meme = "RESSOURCES/parkour.jpg"
bg_fast = "RESSOURCES/warning.gif"
gif = "RESSOURCES/squirrel-dancing-squirrel_2.gif"
fun_bool = True


class Ui(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('GUI.ui', self)

        # Verknüpfung der Widgets aus der GUI
        self.rb_gui_control = self.findChild(QtWidgets.QRadioButton, 'rbGUISteuerung')
        self.rb_controller_control = self.findChild(QtWidgets.QRadioButton, 'rbControllerSteuerung')
        self.rb_normal = self.findChild(QtWidgets.QRadioButton, 'rbNormalBetrieb')
        self.rb_parkour = self.findChild(QtWidgets.QRadioButton, 'rbHindernisBetrieb')
        self.rb_fast = self.findChild(QtWidgets.QRadioButton, 'rbSchnellBetrieb')
        self.s_speed = self.findChild(QtWidgets.QSlider, 'vsGeschwindigkeit')
        self.d_angle = self.findChild(QtWidgets.QDial, 'dWinkel')
        self.l_direction = self.findChild(QtWidgets.QLabel, 'lRichtung')
        self.l_speed = self.findChild(QtWidgets.QLabel, 'lGeschwindigkeit')
        self.pte_input_field = self.findChild(QtWidgets.QPlainTextEdit, 'pTEDialogfensterInput')
        self.pte_output_field = self.findChild(QtWidgets.QPlainTextEdit, 'pTEDialogfensterOutput')
        self.l_background = self.findChild(QtWidgets.QLabel, 'lBackground')
        self.l_input = self.findChild(QtWidgets.QLabel, 'lInput')
        self.l_output = self.findChild(QtWidgets.QRadioButton, 'lOutput')
        self.pb_start = self.findChild(QtWidgets.QPushButton, 'pbStart')
        self.pb_reconnect = self.findChild(QtWidgets.QPushButton, 'pbReconnect')
        self.pb_stop = self.findChild(QtWidgets.QPushButton, 'pbStop')

        # Controller erzeugen, Client zur Kommunikation erzeugen
        self.control = controller.Controller()
        self.st = steuerung.Steuerung()
        # weitere Variablen
        self.send_data = 0
        self.receive_data = 0
        self.num_msg_out = 0
        self.num_msg_in = 0
        self.round_figure = 2
        self.max_msg = 100

        # Worker Thread erstellen
        self.worker = worker.Worker(self.control)
        # Signale verbinden
        self.worker.set_slider_pos_sig.connect(self.set_slider)
        self.worker.do_communication_sig.connect(self.communication)
        self.worker.set_control_to_gui_sig.connect(self.set_gui_control)
        self.worker.set_control_to_controller_sig.connect(self.set_controller_control)
        self.worker.set_mode_normal_sig.connect(self.set_mode_normal)
        self.worker.set_mode_parkour_sig.connect(self.set_mode_parkour)
        self.worker.set_mode_fast_sig.connect(self.set_mode_fast)
        # Thread starten
        self.worker.start()

        # Widgets einstellen
        if self.control.get_controller() is None:
            self.rb_gui_control.setChecked(True)
        self.s_speed.valueChanged.connect(self.set_label)
        self.d_angle.valueChanged.connect(self.set_label)
        self.rb_gui_control.toggled.connect(self.send_gui_control_method)
        self.rb_controller_control.toggled.connect(self.send_gui_control_method)
        self.l_background.setStyleSheet("background-image : url(" + bg_normal + "); background-position: center;")
        self.rb_normal.toggled.connect(self.update_background)
        self.rb_fast.toggled.connect(self.update_background)
        self.rb_parkour.toggled.connect(self.update_background)
        self.pb_stop.clicked.connect(self.stop)
        self.pb_start.clicked.connect(self.start)
        self.pb_reconnect.clicked.connect(self.worker.controller_reconnect)

        # Gif abspielen ( am Anfang noch nicht zeigen )
        if fun_bool:
            self.l_squirrel = self.findChild(QtWidgets.QLabel, 'lSquirrel')
            self.movie = QMovie(gif)
            self.l_squirrel.setMovie(self.movie)
            self.l_squirrel.close()
            self.movie.start()

        # Fenster zeigen
        self.show()

    def start(self):
        if self.control.get_controller() is not None:
            self.control.start_thread()
        self.worker.start_work()

    def stop(self):
        self.control.stop_thread()
        self.worker.stop_work()

    def send_gui_control_method(self):
        if self.control.get_controller() is not None:
            self.worker.set_controller_control(self.rb_controller_control.isChecked())
        else:
            self.rb_gui_control.setChecked(True)

    def communication(self):
        # Senden und empfangen der Daten
        self.send_data = [abs(round(self.get_speed() / 100, self.round_figure)), math.radians(self.get_direction()), self.get_mode()]
        self.st.send_data(self.send_data)
        self.receive_data = self.st.get_data()

        # Gesendete und empfangene Daten anzeigen
        com = "Laenge: " + str(self.send_data[0]) + "\tWinkel: " + str(self.send_data[1]) + "\tMode: " + self.send_data[2]
        self.num_msg_out = self.add_msg_to_output_field(com, self.num_msg_out)
        self.num_msg_in = self.add_msg_to_input_field(str(self.receive_data), self.num_msg_in)

    def set_label(self):
        # aktuelle Werte der Slider in Label schreiben
        self.l_speed.setText("Geschwindigkeit: " + str(self.s_speed.value()))
        self.l_direction.setText("Richtung: " + str(abs(self.d_angle.value())) + "°")

    def set_slider(self, x, y, speed):
        # Slider auf übergebene Werte setzen
        self.s_speed.setValue(int(speed * 100))
        self.d_angle.setValue(int(math.degrees(math.atan2(x, y))))

    # Getter und Setter
    def get_direction(self):
        return self.d_angle.value()

    def get_speed(self):
        return self.s_speed.value()

    def is_gui_control(self):
        return self.rb_gui_control.isChecked()

    def set_gui_control(self):
        self.rb_gui_control.setChecked(True)

    def is_controller_control(self):
        return self.rb_controller_control.isChecked()

    def set_controller_control(self):
        self.rb_controller_control.setChecked(True)

    def get_mode(self):
        if self.rb_normal.isChecked():
            return "Dreieck"
        if self.rb_parkour.isChecked():
            return "Rechteck"
        if self.rb_fast.isChecked():
            return "Fast"

    def update_background(self):
        if self.rb_normal.isChecked():
            # Gif nicht mehr anzeigen, Background ändern
            self.l_background.setStyleSheet("background-image : url(" + bg_normal + "); background-position: center;")
            if fun_bool:
                self.l_squirrel.close()
        elif self.rb_parkour.isChecked():
            # Gif nicht mehr anzeigen, Background ändern
            self.l_background.setStyleSheet(
                "background-image : url(" + bg_parkour + "); background-position: center;")
            if fun_bool:
                self.l_squirrel.close()
                self.l_background.setStyleSheet(
                    "background-image : url(" + bg_parkour_meme + "); background-position: center;")
        elif self.rb_fast.isChecked():
            # Gif anzeigen, Background ändern
            self.l_background.setStyleSheet("background-image : url(" + bg_fast + "); background-position: center;")
            if fun_bool:
                self.l_squirrel.show()

    def set_mode_normal(self):
        self.rb_normal.setChecked(True)
        self.update_background()

    def set_mode_parkour(self):
        self.rb_parkour.setChecked(True)
        self.update_background()

    def set_mode_fast(self):
        self.rb_fast.setChecked(True)
        self.update_background()

    def add_msg_to_output_field(self, com, i):
        # übergebene Daten in Outputfeld anzeigen, wenn zu viele Daten angezeigt werden, Anzeige löschen
        i += 1
        if i > self.max_msg:
            self.pte_output_field.clear()
            i = 0
        self.pte_output_field.appendPlainText(com)
        return i

    def add_msg_to_input_field(self, com, i):
        # übergebene Daten in Inputfeld anzeigen, wenn zu viele Daten angezeigt werden, Anzeige löschen
        i += 1
        if i > self.max_msg:
            self.pte_input_field.clear()
            i = 0
        self.pte_input_field.appendPlainText(com)
        return i


if __name__ == '__main__':
    # GUI erzeugen und starten
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())
