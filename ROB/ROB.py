# ------------------------------------------------------------
# |                         Imports                          |
# ------------------------------------------------------------


# -------------------------Packages---------------------------
import copy as cp
import math
from time import sleep, perf_counter

import numpy as np

# Für das Deepcopy der Trajektorienliste
# Für die Berechnung der Periodenlänge, der Hauptiteration
# Für die Rechnungen mit Matritzen
# Für die Rechnungen mit den Matritzen


# -------------------------Py Scripts-------------------------<
import ROB.HexaplotSender as hxpS
import LEG.Leg as Leg
import ZMQ.server

# Für das Senden der Fußpunkte an die Hexapod-Simulation
# Für die Steuerung der sechs Beine (Dummy-Klasse)
# Für das Starten des Servers auf dem Roboter


class Robot:
    """ Klasse Roboter zur Verarbeitung der Befehle des Controllers und zur Weiterübertragung an die Beine. """

    def __init__(self):
        """
        Robot() -> Object

        Konstruktor der Klasse Robot()
        """

        self.debug = False
        self.simulation = True

        # ---------------------Class Objects----------------------

        self.sv = server.Server()
        """ Objekt der Klasse Server zum Starten des Servers auf dem Roboter. """
        [[0.160, 0.087], [0.160, -0.087], [0, 0.1615], [-0.160, -0.087], [-0.160, 0.087], [0, -0.1615]]
        # Leg 1
        self.leg_v_r = Leg.Leg([0.042, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092], [0.033, 0.032], 0, [14,16,18],[math.pi/4,0,math.pi/2])
        """ Beinobjekt für das Bein vorne rechts, mit den Offset Koordinaten  (7, 8.5, 0). """
        self.offset_v_r = [0.160, 0.087]

        # Leg 2
        self.leg_v_l = Leg.Leg([0.042, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092], [0.033, -0.032], 0, [13,15,17],[-math.pi/4,0,math.pi/2])
        """ Beinobjekt für das Bein vorne links,  mit den Offset Koordinaten  (3, 8.5, 0). """


        # Leg 3
        self.leg_m_l = Leg.Leg([0.032, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092], [0, -0.0445], math.pi/2, [7,9,11],[0,0,math.pi/2])
        """ Beinobjekt für das Bein mitte links,  mit den Offset Koordinaten  (1,   5, 0). """


        # leg 4
        self.leg_h_l = Leg.Leg([0.042, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092], [-0.033, -0.032], math.pi, [1,3,5],[math.pi/4,0,math.pi/2])
        """ Beinobjekt für das Bein hinten links, mit den Offset Koordinaten  (3, 1.5, 0). """


        # leg 5
        self.leg_h_r = Leg.Leg([0.042, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092], [-0.033, 0.032], math.pi, [2,4,6],[-math.pi/4,0,math.pi/2])
        """ Beinobjekt für das Bein hinten rechts, mit den Offset Koordinaten (7, 1.5, 0). """


        # Leg 6
        self.leg_m_r = Leg.Leg([0.032, 0.038, 0.049, 0.059, 0.021, 0.013, 0.092], [0, 0.0445], -math.pi/2, [8,10,12],[0,0,math.pi/2])
        """ Beinobjekt für das Bein mitte rechts, mit den Offset Koordinaten  (9,   5, 0). """


        if self.simulation:
            self.sender = hxpS.HexaplotSender()
            """ Objekt der Klasse HexaplotSender zum Senden der Fußpunkte an die Simulation. """

        # --------------------Class Variables----------------------

        self.all_legs = [self.leg_v_r, self.leg_v_l, self.leg_m_l, self.leg_h_l, self.leg_h_r, self.leg_m_r]
        """ Liste mit allen Beinobjekten. """
        self.group_a = [self.leg_v_l, self.leg_m_r, self.leg_h_l]
        """ Liste mit den schwingenden  Beintrio-Objekten. """
        self.group_b = [self.leg_v_r, self.leg_m_l, self.leg_h_r]
        """ Liste mit den stemmendenden Beintrio-Objekten. """


        self.traj = []

        self.traj_dreieck = [[0.5, 0, 0.5], [1, 0, 0], [0.5, 0, 0],
                             [0, 0, 0], [-0.5, 0, 0], [-1, 0, 0], [-0.5, 0, 0.5], [0, 0, 1]]

        self.traj_rechteck = [[1, 0, 1], [1, 0, 0], [0.5, 0, 0], [0, 0, 0],
                              [-0.5, 0, 0], [-1, 0, 0], [-1, 0, 1], [0, 0, 1]]

        self.traj_fast = [[1, 0, 0.5], [0.5, 0, 0.5],
                          [0, 0, 0.5], [-0.5, 0, 0.5], [-1, 0, 0.5], [0, 0, 0.8]]
        """ Trajektorienliste, für die Fußpunkte von einem Bein, ausgehend vom Ursprung (Defaultgangart = Parabelform) """

        self.cycle_time = 0.4
        """ Zykluszeit für die Abfrage auf neue Befehle. (Defaultwert = 400ms) """
        self.height = 0.071
        """ Höhe für die Berechnung der Trajektorienpunkte. (Defaultwert = 15.1cm) """
        self.pace_type = "Dreieck"
        """ Gangart des Roboters. (Defaultgangart = Dreieck) """
        self.speed = 1
        """ Geschwindigkeit mit der sich der Roboter bewegen soll. (Defaultgeschwindigkeit = 0.4) """
        self.radius = 0.07
        """ Radius vom Arbeitsbereich eines Beines. (Defaultradius = 7cm) """

        #TODO
        # - Geschwindigkeit an Servo
        # - Arbeitsradius experimentell bestimmen

    # -------------------------Methods-----------------------------
    def iterate(self):
        """
        iterate() -> None

        Die Hauptmethode, welche auf dem Roboter gestartet wird.
        Diese hat eine Endlosschleife, welche die fortlaufenden Befehle des Clienten verarbeitet.
        """
        for legs in self.group_a:
            legs.setPosition(self.leg_v_l.convert([0, 0, self.height], True))
        for legs in self.group_b:
            legs.setPosition(self.leg_v_l.convert([0, 0, 0], True))
        if self.simulation:
            print(self.leg_v_l.getPosition())
            self.sender.send_points([[self.leg_v_l.convert(self.leg_v_l.getPosition()), [0.033,-0.032,self.height]],
                                     [self.leg_v_l.convert(self.leg_v_r.getPosition()), [0.033,0.032,self.height]],
                                     [self.leg_v_l.convert(self.leg_m_l.getPosition()), [0.0,-0.0445,self.height]],
                                     [self.leg_v_l.convert(self.leg_h_l.getPosition()), [-0.033,-0.032,self.height]],
                                     [self.leg_v_l.convert(self.leg_h_r.getPosition()), [-0.033,0.032,self.height]],
                                     [self.leg_v_l.convert(self.leg_m_r.getPosition()), [0.0,0.0445,self.height]]])

        schwingpunkt = 0
        while 1:
            t_start = perf_counter()

            if schwingpunkt == 0 or schwingpunkt == int(len(self.traj) / 2):
                n_commands = self.get_new_commands()
                if n_commands != 0:
                    speed, angle, pace_type = n_commands[0], n_commands[1], n_commands[2]
                    if speed == 0:
                        continue
                    if pace_type == "Rechteck":
                        self.traj = self.traj_rechteck
                        self.pace_type = "Rechteck"
                    elif pace_type == "Fast":
                        self.traj = self.traj_fast
                        self.pace_type = "Fast"
                    else:
                        self.traj = self.traj_dreieck
                        self.pace_type = "Dreieck"
                    self.traj = self.calc_tray_list(self.traj, length=self.radius, height=self.height)
                    for legs in self.all_legs:
                       legs.motors[0].setSpeedValue(40)
                       legs.motors[1].setSpeedValue(40)
                       legs.motors[2].setSpeedValue(40)

                    self.traj = self.set_direction(self.traj, angle)
                    if self.debug:
                        print(self.traj)
                    self.traj = self.traj.tolist()
                else:
                    continue
            elif schwingpunkt == len(self.traj):
                schwingpunkt = 0
                continue
            stemmpunkt = schwingpunkt + len(self.traj) / 2

            if stemmpunkt >= len(self.traj):
                stemmpunkt = stemmpunkt - len(self.traj)

            stemmpunkt = int(stemmpunkt)
            for legs in self.group_a:
                legs.setPosition(self.leg_v_l.convert(self.traj[schwingpunkt], True))
            for legs in self.group_b:
                legs.setPosition(self.leg_v_l.convert(self.traj[stemmpunkt], True))
            if self.simulation:
                self.sender.send_points([[self.leg_v_l.convert(self.leg_v_l.getPosition()), [0.033,-0.032,self.height]],
                                         [self.leg_v_l.convert(self.leg_v_r.getPosition()), [0.033,0.032,self.height]],
                                         [self.leg_v_l.convert(self.leg_m_l.getPosition()), [0.0,-0.0445,self.height]],
                                         [self.leg_v_l.convert(self.leg_h_l.getPosition()), [-0.033,-0.032,self.height]],
                                         [self.leg_v_l.convert(self.leg_h_r.getPosition()), [-0.033,0.032,self.height]],
                                         [self.leg_v_l.convert(self.leg_m_r.getPosition()), [0.0,0.0445,self.height]]])

            schwingpunkt += 1
            t_end = perf_counter()
            period_length = t_end - t_start
            sleep(self.cycle_time - period_length)

            if self.debug:
                print(period_length)

    @staticmethod
    def calc_tray_list(org_traj, offset=None, length=1.0, height=1.0):
        """
        calc_tray_list(traj: List[List[x: float,y: float,z: float]], coord: tuple(x,y,z), length: float, height: float) -> None

        Eine Methode zum berechnen einer neuen Trajektorienliste, mit einer anderen Höhe, Länge oder Startposition.
        """

        traj = cp.deepcopy(org_traj)
        if offset is None:
            offset = [0, 0, 0]
        print(offset)
        for point in traj:
            point[0] = point[0] * length + offset[0]
            point[1] = point[1] * length + offset[1]
            point[2] = point[2] * height + offset[2]
        return traj

    @staticmethod
    def rotation_z(teta):
        """
        calc_tray_line(teta: float) -> numpy.matrix()

        Eine statische Methode zum berechnen einer Rotationsmatrix um die Z-Achse, mit dem Winkel Teta
        """
        rz_matrix = np.matrix([[math.cos(teta), -1 * math.sin(teta), 0],
                               [math.sin(teta), math.cos(teta), 0],
                               [0, 0, 1]])
        return rz_matrix

    def set_direction(self, org_traj, angle):
        """
        set_direction(Org_traj: List(), angle: float) -> numpy.matrix()

        Eine Methode zum berechnen der neuen Trajektorienliste, verschoben um die z-Achse mit der Variable Angle.
        """
        traj = np.matrix(cp.deepcopy(org_traj))
        for i in range(0, len(traj)):
            traj[i] = traj[i] * self.rotation_z(angle)
        return traj

    def get_new_commands(self, command=None):
        """
        get_new_command(command: List[tuple(x: float,y: float),speed: float,pacetype: str]) -> List[tuple(x: float,y: float),speed: float,pacetype: str]

        Eine Methode zum Abfangen der Daten vom Clienten oder auch zum Eingeben eigener Befehle über die Methode
        """
        if not command:
            command = self.sv.get_data()

        if self.debug:
            typ = type(command)
            print(command)
            print(typ)
        return command  # [Geschwindigkeit, Winkel,Gangart]

    def startup(self):
        self.leg_v_l.motors[0].setDesiredJointAngle()


if __name__ == "__main__":
    rob = Robot()
    rob.iterate()
