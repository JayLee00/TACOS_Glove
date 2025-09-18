import time
import os, sys
sys.path.append(os.getcwd())
from Tactile.Serial.tactile_serial import Tactile_Serial

class Tactile:
    def __init__(self, port='COM10'):
        self.t_ser = Tactile_Serial(port=port)
        self.t_ser.open()

        self.start_read()

    def start_read(self):
        self.t_ser.start_read_loop()

    def print_sensor_data(self, timestamp_en = False):
        if timestamp_en:
            print(self.t_ser.timestamp)
        print(self.t_ser.vals)

    def get_sensor_data(self) -> list:
        return self.t_ser.vals

if __name__ == "__main__":
    t = Tactile()
    while True:
        t.print_sensor_data()