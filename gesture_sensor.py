#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
import time
import smbus2 as smbus
import logging
import logging.handlers
import argparse
import sys
import os
from dotenv import load_dotenv
from hassapi import Hass

load_dotenv()
HASSURL = os.getenv('HASSURL')
HASSTOKEN = os.getenv('HASSTOKEN')
hass = Hass(hassurl=HASSURL, token=HASSTOKEN)

EVENTNAME = os.getenv('GESTURE_EVENTNAME', "pi4gesture")
DELAY = os.getenv('GESTURE_DELAY', 0.05)

#i2c address
PAJ7620U2_I2C_ADDRESS   = 0x73
#Register Bank select
PAJ_BANK_SELECT			= 0xEF			#Bank0== 0x00,Bank1== 0x01
#Register Bank 0
PAJ_SUSPEND				= 0x03		#I2C suspend command (Write = 0x01 to enter suspend state). I2C wake-up command is slave ID wake-up. Refer to topic “I2C Bus Timing Characteristics and Protocol”
PAJ_INT_FLAG1_MASK		= 0x41		#Gesture detection interrupt flag mask
PAJ_INT_FLAG2_MASK		= 0x42		#Gesture/PS detection interrupt flag mask
PAJ_INT_FLAG1		    = 0x43		#Gesture detection interrupt flag
PAJ_INT_FLAG2			= 0x44		#Gesture/PS detection interrupt flag
PAJ_STATE				= 0x45		#State indicator for gesture detection (Only functional at gesture detection mode)
PAJ_PS_HIGH_THRESHOLD	= 0x69		#PS hysteresis high threshold (Only functional at proximity detection mode)		
PAJ_PS_LOW_THRESHOLD	= 0x6A		#PS hysteresis low threshold (Only functional at proximity detection mode)
PAJ_PS_APPROACH_STATE	= 0x6B		#PS approach state,  Approach = 1 , (8 bits PS data >= PS high threshold),  Not Approach = 0 , (8 bits PS data <= PS low threshold)(Only functional at proximity detection mode)
PAJ_PS_DATA				= 0x6C		#PS 8 bit data(Only functional at gesture detection mode)
PAJ_OBJ_BRIGHTNESS		= 0xB0		#Object Brightness (Max. 255)
PAJ_OBJ_SIZE_L			= 0xB1		#Object Size(Low 8 bit)		
PAJ_OBJ_SIZE_H			= 0xB2		#Object Size(High 8 bit)	
#Register Bank 1
PAJ_PS_GAIN				= 0x44	    #PS gain setting (Only functional at proximity detection mode)
PAJ_IDLE_S1_STEP_L		= 0x67		#IDLE S1 Step, for setting the S1, Response Factor(Low 8 bit)
PAJ_IDLE_S1_STEP_H		= 0x68		#IDLE S1 Step, for setting the S1, Response Factor(High 8 bit)	
PAJ_IDLE_S2_STEP_L		= 0x69		#IDLE S2 Step, for setting the S2, Response Factor(Low 8 bit)
PAJ_IDLE_S2_STEP_H		= 0x6A		#IDLE S2 Step, for setting the S2, Response Factor(High 8 bit)
PAJ_OPTOS1_TIME_L		= 0x6B		#OPtoS1 Step, for setting the OPtoS1 time of operation state to standby 1 state(Low 8 bit)	
PAJ_OPTOS2_TIME_H		= 0x6C		#OPtoS1 Step, for setting the OPtoS1 time of operation state to standby 1 stateHigh 8 bit)	
PAJ_S1TOS2_TIME_L		= 0x6D		#S1toS2 Step, for setting the S1toS2 time of standby 1 state to standby 2 state(Low 8 bit)	
PAJ_S1TOS2_TIME_H		= 0x6E		#S1toS2 Step, for setting the S1toS2 time of standby 1 state to standby 2 stateHigh 8 bit)	
PAJ_EN					= 0x72		#Enable/Disable PAJ7620U2
#Gesture detection interrupt flag
PAJ_UP				    = 0x01 
PAJ_DOWN			    = 0x02
PAJ_LEFT			    = 0x04 
PAJ_RIGHT			    = 0x08
PAJ_FORWARD		    	= 0x10 
PAJ_BACKWARD		    = 0x20
PAJ_CLOCKWISE			= 0x40
PAJ_COUNT_CLOCKWISE		= 0x80
PAJ_WAVE				= 0x100
#Power up initialize array
Init_Register_Array = (
	(0xEF,0x00),
	(0x37,0x07),
	(0x38,0x17),
	(0x39,0x06),
	(0x41,0x00),
	(0x42,0x00),
	(0x46,0x2D),
	(0x47,0x0F),
	(0x48,0x3C),
	(0x49,0x00),
	(0x4A,0x1E),
	(0x4C,0x20),
	(0x51,0x10),
	(0x5E,0x10),
	(0x60,0x27),
	(0x80,0x42),
	(0x81,0x44),
	(0x82,0x04),
	(0x8B,0x01),
	(0x90,0x06),
	(0x95,0x0A),
	(0x96,0x0C),
	(0x97,0x05),
	(0x9A,0x14),
	(0x9C,0x3F),
	(0xA5,0x19),
	(0xCC,0x19),
	(0xCD,0x0B),
	(0xCE,0x13),
	(0xCF,0x64),
	(0xD0,0x21),
	(0xEF,0x01),
	(0x02,0x0F),
	(0x03,0x10),
	(0x04,0x02),
	(0x25,0x01),
	(0x27,0x39),
	(0x28,0x7F),
	(0x29,0x08),
	(0x3E,0xFF),
	(0x5E,0x3D),
	(0x65,0x96),
	(0x67,0x97),
	(0x69,0xCD),
	(0x6A,0x01),
	(0x6D,0x2C),
	(0x6E,0x01),
	(0x72,0x01),
	(0x73,0x35),
	(0x74,0x00),
	(0x77,0x01),
)
#Approaches register initialization array
Init_PS_Array = (
	(0xEF,0x00),
	(0x41,0x00),
	(0x42,0x00),
	(0x48,0x3C),
	(0x49,0x00),
	(0x51,0x13),
	(0x83,0x20),
	(0x84,0x20),
	(0x85,0x00),
	(0x86,0x10),
	(0x87,0x00),
	(0x88,0x05),
	(0x89,0x18),
	(0x8A,0x10),
	(0x9f,0xf8),
	(0x69,0x96),
	(0x6A,0x02),
	(0xEF,0x01),
	(0x01,0x1E),
	(0x02,0x0F),
	(0x03,0x10),
	(0x04,0x02),
	(0x41,0x50),
	(0x43,0x34),
	(0x65,0xCE),
	(0x66,0x0B),
	(0x67,0xCE),
	(0x68,0x0B),
	(0x69,0xE9),
	(0x6A,0x05),
	(0x6B,0x50),
	(0x6C,0xC3),
	(0x6D,0x50),
	(0x6E,0xC3),
	(0x74,0x05),
)
#Gesture register initializes array
Init_Gesture_Array = (
	(0xEF,0x00),
	(0x41,0x00),
	(0x42,0x00),
	(0xEF,0x00),
	(0x48,0x3C),
	(0x49,0x00),
	(0x51,0x10),
	(0x83,0x20),
	(0x9F,0xF9),
	(0xEF,0x01),
	(0x01,0x1E),
	(0x02,0x0F),
	(0x03,0x10),
	(0x04,0x02),
	(0x41,0x40),
	(0x43,0x30),
	(0x65,0x96),
	(0x66,0x00),
	(0x67,0x97),
	(0x68,0x01),
	(0x69,0xCD),
	(0x6A,0x01),
	(0x6B,0xB0),
	(0x6C,0x04),
	(0x6D,0x2C),
	(0x6E,0x01),
	(0x74,0x00),
	(0xEF,0x00),
	(0x41,0xFF),
	(0x42,0x01),
)

# Deafults
LOG_FILENAME = "/home/homeassistant/gesture/gesture_sensor.log"
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"

# Define and parse command line arguments
parser = argparse.ArgumentParser(description="Simple service for homeassistant sensor")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")

# If the log file is specified on the command line then override the default
args = parser.parse_args()
if args.log:
        LOG_FILENAME = args.log

# Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
# Give the logger a unique name (good practice)
logger = logging.getLogger(__name__)
# Set the log level to LOG_LEVEL
logger.setLevel(LOG_LEVEL)
# Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
# Format each log message like this
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
# Attach the formatter to the handler
handler.setFormatter(formatter)
# Attach the handler to the logger
logger.addHandler(handler)



# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

# Replace stdout with logging to file at INFO level
sys.stdout = MyLogger(logger, logging.INFO)
# Replace stderr with logging to file at ERROR level
sys.stderr = MyLogger(logger, logging.ERROR)






class PAJ7620U2(object):
	def __init__(self,address=PAJ7620U2_I2C_ADDRESS):
		self._address = address
		self._bus = smbus.SMBus(6)
		time.sleep(0.5)
		if self._read_byte(0x00) == 0x20:
			print("\nGesture Sensor OK\n")
			for num in range(len(Init_Register_Array)):
				self._write_byte(Init_Register_Array[num][0],Init_Register_Array[num][1])
		else:
			print("\nGesture Sensor Error\n")
		self._write_byte(PAJ_BANK_SELECT, 0)
		for num in range(len(Init_Gesture_Array)):
				self._write_byte(Init_Gesture_Array[num][0],Init_Gesture_Array[num][1])
	def _read_byte(self,cmd):
		return self._bus.read_byte_data(self._address,cmd)
	
	def _read_u16(self,cmd):
		LSB = self._bus.read_byte_data(self._address,cmd)
		MSB = self._bus.read_byte_data(self._address,cmd+1)
		return (MSB	<< 8) + LSB
	def _write_byte(self,cmd,val):
		self._bus.write_byte_data(self._address,cmd,val)
	def check_gesture(self):
		Gesture_Data=self._read_u16(PAJ_INT_FLAG1)
		if Gesture_Data == PAJ_UP:
			logger.info("Up\r\n")
			hass.fire_event(EVENTNAME, {"action": "up"})
		elif Gesture_Data == PAJ_DOWN:
			logger.info("Down\r\n")
			hass.fire_event(EVENTNAME, {"action": "down"})
		elif Gesture_Data == PAJ_LEFT:
			logger.info("Left\r\n")	
			hass.fire_event(EVENTNAME, {"action": "left"})
		elif Gesture_Data == PAJ_RIGHT:
			logger.info("Right\r\n")	
			hass.fire_event(EVENTNAME, {"action": "right"})
		elif Gesture_Data == PAJ_FORWARD:
			logger.info("Forward\r\n")	
			hass.fire_event(EVENTNAME, {"action": "forward"})
		elif Gesture_Data == PAJ_BACKWARD:
			logger.info("Backward\r\n")
			hass.fire_event(EVENTNAME, {"action": "backward"})
		elif Gesture_Data == PAJ_CLOCKWISE:
			logger.info("Clockwise\r\n")	
			hass.fire_event(EVENTNAME, {"action": "clockwise"})
		elif Gesture_Data == PAJ_COUNT_CLOCKWISE:
			logger.info("AntiClockwise\r\n")	
			hass.fire_event(EVENTNAME, {"action": "counterclockwise"})
		elif Gesture_Data == PAJ_WAVE:
			logger.info("Wave\r\n")	
			hass.fire_event(EVENTNAME, {"action": "wave"})
		return Gesture_Data

if __name__ == '__main__':
	
	import time
    
	logger.info("\nGesture Sensor Test Program ...\n")
	#print("\nGesture Sensor Test Program ...\n")
	while True:
		try:
			paj7620u2=PAJ7620U2()
		except SomeSpecificException:
			continue
		break	

	while True:
		time.sleep(0.05)
		paj7620u2.check_gesture()
		





