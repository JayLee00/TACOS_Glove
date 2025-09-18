import serial
from serial import SerialException, SerialTimeoutException
import time
import threading

# from MoCAP.Manager.man_enum import HandSide

# class Tactile:
#     def __init__(self, handside: HandSide):
#         handside = handside