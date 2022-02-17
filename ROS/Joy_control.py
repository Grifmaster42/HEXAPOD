#!/usr/bin/env python3
import rospy
import math 
from rospy.topics import Publisher
from beginner_tutorials.msg import transfer
from sensor_msgs.msg import Joy


class controller:
	def __init__(self):		
		self.rosPub = rospy.Publisher('ControllerInput', transfer, queue_size = 1)
		rospy.init_node('Controller', anonymous=True)
		rospy.Subscriber("joy", Joy, self.callback)
		self.speed = 0.0
		self.angle = 0.0
		self.button = 0
		
	def callback(self,data):
		
		self.xAxes = round(data.axes[1], 2)	#x Achsenposition des L. Sticks auf 2 Nachkommastellen gerundet
		self.yAxes = round(data.axes[0], 2)	#y Achsenposition des L. Sticks auf 2 Nachkommastellen gerundet
		
		message = transfer()
		message.speed = math.sqrt(self.xAxes**2+self.yAxes**2)		#Umrechnung auf Geschwindigkeit aus den Achsenpositionen des l. Stock
		message.angle = math.atan2(self.yAxes,self.xAxes)/math.pi		#Umrechnung auf Bogenmaß aus den Achsenpositionen des l. Stock
		
		message.speed = round(message.speed, 2)	#x Achsenposition des L. Sticks auf 2 Nachkommastellen gerundet
		message.angle = round(message.angle, 2)	#y Achsenposition des L. Sticks auf 2 Nachkommastellen gerundet

		#data.buttons[0] -> Knopf A
		#data.buttons[1] -> Knopf B
		#data.buttons[2] -> Knopf X
		#data.buttons[3] -> Knopf Y
		
		#Knopf A wird gedrückt
		if data.buttons[0] == 1 and data.buttons[1] == 0 and data.buttons[2] == 0 and data.buttons[3] == 0:
			message.button = 1
		 #Knopf B wird gedrückt 
		elif data.buttons[0] == 0 and data.buttons[1] == 1 and data.buttons[2] == 0 and data.buttons[3] == 0:
			message.button = 2
		 #Knopf X wird gedrückt
		elif data.buttons[0] == 0 and data.buttons[1] == 0 and data.buttons[2] == 1 and data.buttons[3] == 0:
			message.button = 3
		 #Knopf Y wird gedrückt
		elif data.buttons[0] == 0 and data.buttons[1] == 0 and data.buttons[2] == 0 and data.buttons[3] == 1:
			message.button = 4
		#Kein Knopf wird gedrückt
		elif data.buttons[0] == 0 and data.buttons[1] == 0 and data.buttons[2] == 0 and data.buttons[3] == 0:
			message.button = 0
		#Es werden mehrere Knöpfe gleichzeitig gedrückt
		else:
			message.button = -1
			rospy.loginfo('ERR: [Button] Keine eindeutige Eingabe!')
		self.rosPub.publish(message)
		rospy.loginfo('Speed: ' + str(message.speed))
		rospy.loginfo('Angle: ' + str(message.angle)+ ' ' + str(round(math.degrees(message.angle*math.pi),1)))
		rospy.loginfo('Button: ' + str(message.button))
		rospy.loginfo('-------------------')
	
if __name__ == '__main__':
	controller()
	rospy.spin()
