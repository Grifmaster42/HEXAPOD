from DRIVE.serialPorts import *
import copy


# QUESTIONS:
#     -How to read/write words of data? For Bulk Read and Sync Write?
#     -do error handling
#     -do checksum control


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
    __DYNAMIXEL_PORT_NR = 22  # Index of dynamixel line in list
    __BAUDRATE = 1000000  # Baudrate of dynamixel serial line
    __TIME_OUT_DEFAULT = 2  # Default time out
    __DIRECT_ACTION = 3  # Direct action command
    __TRIGGERT_ACTION = 4  # Triggered action command
    __STATUS_PACKET_BASE_LENGTH = 6  # Base length of status packet
    __lines = serialPortList()  # Contains all available serial lines
    # print("dyn port", __lines)
    __serial_port = serial.Serial(__lines[__DYNAMIXEL_PORT_NR],
                                  __BAUDRATE, timeout=__TIME_OUT_DEFAULT)  # Serial line object
    # Create templates of command packets 
    __pktAction = [255, 255, 0, 2, 5, 0]  # Packet to invoke action
    __pktReadData = [255, 255, 0, 4, 2, 0, 0, 0]  # Packet to request date
    __pktWriteByte = [255, 255, 0, 4, 3, 0, 0, 0]  # Packet to write byte
    __pktWriteNByte = [255, 255, 0, 0, 3, 0, 0]  # Base-packet to write n-bytes
    __pktWriteWord = [255, 255, 0, 7, 3, 0, 0]  # Packet to write word

    # ---------------------------------------------------------------------------
    # Definition of private methods with implicit servo-id
    # Accessible only within own class
    # ---------------------------------------------------------------------------
    # Constructor, sets id and defines error variable
    # id -> id of attached servo
    def __init__(self, id, prt):
        self.id = id
        self.error = 0
        self.prt = prt

    # Calculates check sum of packet list
    def __checkSum(self, pkt):
        s = sum(pkt[2:-1])
        return (~s) & 0xFF

    # Start predefined action on servo
    # execute the registered Reg Write instruction
    # id -> id of servo to ping, without id -> broadcast action
    def __doAction(self, id):
        pktAction = copy.deepcopy(self.__pktAction)  # copy base pkt

        pktAction[2] = id  # place id

        pktAction[-1] = self.__checkSum(pktAction)  # place checksum

        if self.prt:
            print(pktAction)

        self.__serial_port.write(bytearray(pktAction))  # sendCommand

    # Prepares and sends packet to servo in order to read data from servo memory
    # register -> register address of servo
    # nByte    -> number of bytes to read
    # __pktReadData = [255, 255, 0, 4, 2, 0, 0, 0]
    def __writeReadDataPkt(self, register, nByte):
        pktReadData = copy.deepcopy(self.__pktReadData)  # copy base pkt

        pktReadData[2] = self.id  # place id

        # base length 4 always

        pktReadData[5] = register  # place register address

        pktReadData[6] = nByte  # length of data

        pktReadData[7] = self.__checkSum(pktReadData)  # calc check sum

        if self.prt:
            print(pktReadData)

        self.__serial_port.write(bytearray(pktReadData))  # sendCommand

        pktStatus = self.__doReadStatusPkt(self.__STATUS_PACKET_BASE_LENGTH + nByte)

        return pktStatus[(-1 - nByte):-1]

    # Read status packet, set error value and get return values from servo
    # nByte -> number of bytes to read
    def __doReadStatusPkt(self, nByte):
        pktReadStatus = self.__serial_port.read(nByte)  # read status packet of servo

        self.error = pktReadStatus[4]  # set error value with error bit

        return pktReadStatus  # return parameter values of status packet

    # Definition of protected methods
    # Accessible within own and derived classes
    # ---------------------------------------------------------------------------

    # Sends packet to servo in order to write n data bytes into servo memory
    # register -> register address of servo
    # data     -> list of bytes to write
    # trigger  -> False -> command is directly executed, True -> command is delayed until action command
    # __pktWriteNByte = [255, 255, 0, 0, 3, 0, 0]
    # e.g. data = [200,300,1020]
    def _writeNBytePkt(self, register, data, trigger):

        nBytes = len(data)
        pktWriteNByte = copy.deepcopy(self.__pktWriteNByte)
        pktWriteNByte[2] = self.id

        pktWriteNByte.extend([0] * nBytes)  # data byte(s) + register byte

        pktWriteNByte[3] = nBytes + 3  # data bytes + register + 2

        # REG WRITE
        if trigger:
            pktWriteNByte[4] = 4

        pktWriteNByte[5] = register  # register address

        i = 6
        for date in data:
            pktWriteNByte[i] = date
            i += 1

        pktWriteNByte[-1] = self.__checkSum(pktWriteNByte)

        if self.prt:
            print(pktWriteNByte)

        self.__serial_port.write(bytearray(pktWriteNByte))  # write pkt to servo

    # Read data byte from servo memory
    # register -> register address of servo
    # dtLen    -> number of data bytes to read
    # __pktReadData = [255, 255, 0, 4, 2, 0, 0, 0]
    def _requestNByte(self, register, dtLen=1):
        return self.__writeReadDataPkt(register, dtLen)

    def _writeNWordPkt(self, register, data, trigger):

        nBytes = len(data) * 2
        pktWriteNWord = copy.deepcopy(self.__pktWriteWord)  # copy base pkt
        pktWriteNWord[2] = self.id

        pktWriteNWord.extend([0] * nBytes)  # data byte(s) + register byte

        pktWriteNWord[3] = nBytes + 3  # data bytes + register + 2

        # REG WRITE
        if trigger:
            pktWriteNWord[4] = 4

        pktWriteNWord[5] = register  # register address

        i = 6
        for date in data:
            pktWriteNWord[i] = date & 255
            pktWriteNWord[i + 1] = date >> 8
            i += 2

        pktWriteNWord[-1] = self.__checkSum(pktWriteNWord)

        if self.prt:
            print("SEND:" + str(pktWriteNWord))

        self.__serial_port.write(bytearray(pktWriteNWord))  # write pkt to servo

        # Read data word from servo memory
        # register -> register address of servo
        # dtWLen   -> number of data words to read

    def _requestNWord(self, register, dtWlen=1):
        return self.__writeReadDataPkt(register, dtWlen * 2)

    # Definition of public methods with implicit servo-id
    # Accessible from everywere    
    # ---------------------------------------------------------------------------
    # Show available serial lines
    def showSerialLines(self):
        print(Dynamixel.__lines)

    # Start predefined action on servo with assigned id
    def _action(self, id):
        return self.__doAction(id)

    # Get last error    
    def getLastError(self):
        return self.error
