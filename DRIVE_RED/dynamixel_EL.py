import copy

import serial
import serial.tools.list_ports
import DRIVE_RED.serialPorts_EL


# Classdefinition to implement dynamixel protocol
# ===============================================================================
# Implements the dynamixel protocol 1.0
# ------------------------------------------------------------------------------
# Assigns the class object to a dedicated servo by the servo id
# Initializes the serial connection to the servo bus
# Handles the transfer of all required packet types with 1..n data bytes or -words
class Dynamixel:
    # Definition of protected class attributes
    # Accessible only within own and derived classes
    # ---------------------------------------------------------------------------
    _ID_BROADCAST = 0xFE

    # Definition of private class attributes, accessible only within own class
    # ---------------------------------------------------------------------------
    # Define dynamixel constants
    __DYNAMIXEL_PORT_NR = 0  # Index of dynamixel line in list
    __BAUDRATE = 1000000  # Baudrate of dynamixel serial line
    __TIME_OUT_DEFAULT = 2  # Default time out
    __DIRECT_ACTION = 3  # Direct action command
    __TRIGGERT_ACTION = 4  # Triggered action command
    __STATUS_PACKET_BASE_LENGTH = 6  # Base length of status packet
    __lines = DRIVE_RED.serialPorts_EL.serialPortList()  # Contains all available serial lines
    __serial_port = serial.Serial(__lines[__DYNAMIXEL_PORT_NR],\
                                    __BAUDRATE, timeout = __TIME_OUT_DEFAULT)   # Serial line object
    # Create templates of command packets
    __pktAction = [255, 255, 0, 2, 5, 0]  # Packet to invoke action
    __pktReadData = [255, 255, 0, 4, 2, 0, 0, 0]  # Packet to request date
    __pktWriteByte = [255, 255, 0, 4, 3, 0, 0, 0]  # Packet to write byte
    __pktWriteNByte = [255, 255, 0, 0, 3, 0]  # Base-packet to write n-bytes
    __pktWriteWord = [255, 255, 0, 5, 3, 0, 0, 0, 0]  # Packet to write word

    # ---------------------------------------------------------------------------
    # Definition of private methods with implicit servo-id
    # Accessible only within own class
    # ---------------------------------------------------------------------------
    # Constructor, sets id and defines error variable
    # id -> id of attached servo
    def __init__(self, id):
        self.id = id
        self.error = 0


    # Start predefined action on servo
    # id -> id of servo to ping, without id -> broadcast action
    def __doAction(self, id=_ID_BROADCAST):
        packet = copy.copy(self.__pktAction)
        packet[2] = id
        packet[5] = self.__checkSum(packet)

        self.__serial_port.write(packet)


    # Prepares and sends packet to servo in order to read data from servo memory
    # register -> register address of servo
    # nByte    -> number of bytes to read
    def __writeReadDataPkt(self, register, nByte):
        packet = copy.copy(self.__pktReadData)
        packet[2]= self.id
        packet[5] = register
        packet[6] = nByte
        packet[7] = self.__checkSum(packet)
        self.__serial_port.write(packet)
        statuspkt = self.__readStatusPkt(nByte)
        if nByte == 2:
            return statuspkt[-3:-1]
        else:
            return statuspkt[-2]


    # Read status packet, set error value and get return values from servo
    # nByte    -> number of bytes to read
    def __readStatusPkt(self, nByte):
        #statusPaket = self.__doReadStatusPkt()
        statusPaket = self.__serial_port.read(self.__STATUS_PACKET_BASE_LENGTH + nByte)
        self.error = statusPaket[4]
        if self.__checkSum(statusPaket) != statusPaket[-1]:
            print("Checksumme fehlerhaft!: ")
            self.__readStatusPkt(nByte)
        if self.error != 0:
            print("FEHLER!!: ", self.error)
        else:
            pass
        return statusPaket


    # Calculates check sum of packet list
    def __checkSum(self, pkt):
        s = sum(pkt[2:-1])
        return (~s) & 0xFF


#benutzen wir nicht
    # Read status packet, set error value and get return values from servo
    # nByte -> number of bytes to read
    def __doReadStatusPkt(self, nByte):
        statusPaket = self.__serial_port.read()
        self.error = statusPaket[4]
        return self.error


    # Definition of protected methods
    # Accessible within own and derived classes
    # ---------------------------------------------------------------------------
    # Read data byte from servo memory
    # register -> register address of servo
    # dtLen    -> number of data bytes to read
    def _requestNByte(self, register, dtLen=1):
        data = self.__writeReadDataPkt(register,dtLen)
        return data


    # Read data word from servo memory
    # register -> register address of servo
    # dtWLen   -> number of data words to read
    def _requestNWord(self, register, dtWlen=1):
        data = self._requestNByte(register, dtWlen * 2)
        return data


    # Sends packet to servo in order to write n data bytes into servo memory
    # register -> register address of servo
    # data     -> list of bytes to write
    # trigger  -> False -> command is directly executed, True -> command is delayed until action command
    def _writeNBytePkt(self, register, data, trigger):
        packet = copy.copy(self.__pktWriteNByte)
        packet[2] = self.id
        if trigger == False:
            packet[4] = self.__DIRECT_ACTION
        else:
            packet[4] = self.__TRIGGERT_ACTION
        packet[5] = register
        packet.extend(data)
        packet[3] = len(packet[5:]) + 2 # set pkt length
        packet.append(0)
        packet[-1] = self.__checkSum(packet)
        self.__serial_port.write(packet)
        return packet


    # Sends packet to servo in order to write data dword into servo memory
    # register -> register address of servo
    # data     -> list of words to write
    # trigger  -> False -> command is directly executed, True -> command is delayed until action command
    def _writeNWordPkt(self, register, data, trigger):
        byteData = []
        for word in data:
            byteData.append(word & 0xFF)  # append 1st byte
            byteData.append(word >> 8 & 0xFF)  # append 2nd byte
        self._writeNBytePkt(register, byteData, trigger)


    # Definition of public methods with implicit servo-id
    # Accessible from everywere
    # ---------------------------------------------------------------------------
    # Show available serial lines
    def showSerialLines(self):
        print(Dynamixel.__lines)


    # Start predefined action on servo with assigned id
    def action(self):
        self.__doAction(self.id)
        return self.getLastError()


    # Get last error
    def getLastError(self):
        #print("Error:", self.error)
        return self.error

