import time
import threading
import numpy as np
import os, sys
sys.path.append(os.getcwd())
from Tactile.Serial.tactile_serial import Tactile_Serial

class Tactile:
    def __init__(self, port='COM10', baudrate=1_000_000, print_en=False, calib_data=None):
        self.t_ser = Tactile_Serial(port=port, baudrate=baudrate)
        self.prev_cnt = 0
        self.calib_data = calib_data

        self.calibrated_pres = None
        
        self._stop_event = threading.Event()

        self.t_ser.open()
        self.start_read()
        if print_en == True:
            self.start_print_loop()

    def start_read(self):
        self.t_ser.start_read_loop()

    def print_sensor_data(self, timestamp_en = False):
        if timestamp_en:
            print(self.t_ser.timestamp)
        print(self.t_ser.pres)

    def get_all_data(self) -> list:
        return self.t_ser.pres, self.t_ser.temp, self.t_ser.cnt, self.t_ser.data_hz, self.t_ser.miss_cnt
    
    def get_calibrated_data(self) -> list:
        if self.calib_data is not None and len(self.t_ser.pres) != 0:
            self.calibrated_pres = self.t_ser.pres - (self.calib_data["ls_a"] * self.t_ser.temp + self.calib_data["ls_b"])
            return self.calibrated_pres, self.t_ser.temp, self.t_ser.cnt, self.t_ser.data_hz, self.t_ser.miss_cnt
        else:
            return self.t_ser.pres, self.t_ser.temp, self.t_ser.cnt, self.t_ser.data_hz, self.t_ser.miss_cnt
    
    def print_all_data(self):
            while not self._stop_event.is_set():
                # cnt = self.t_ser.cnt
                # if self.prev_cnt != cnt:
                pres_np = np.asarray(self.t_ser.pres, dtype=np.float64).reshape(-1)
                temp_np = np.asarray(self.t_ser.temp, dtype=np.float64).reshape(-1)

                s_pres = np.array2string(
                    pres_np, max_line_width=1_000_000, separator=' ', precision=4, floatmode='maxprec_equal'
                )
                s_temp = np.array2string(
                    temp_np, max_line_width=1_000_000, separator=' ', precision=2, floatmode='maxprec_equal'
                )
                
                print(f"\r{self.t_ser.cnt:5d}: pres={s_pres}, temp={s_temp}\t{self.t_ser.data_hz:.3f} Hz\tmiss={self.t_ser.miss_cnt}")#, end='', flush=True)
                    # self.prev_cnt = self.t_ser.cnt
            # s1 = np.array2string(self.t_ser.pres, max_line_width=100000, threshold=np.inf, separator=' ')
            # s2 = np.array2string(self.t_ser.temp, max_line_width=100000, threshold=np.inf, separator=' ')
            # print(f"{self.t_ser.cnt:5d}: pres={self.t_ser.pres}, temp={self.t_ser.temp}", end="\t")
            # print(f"{self.t_ser.data_hz:.3f} Hz", end="\n")

    def start_print_loop(self):
        if getattr(self, "thread", None) and self.thread.is_alive():
            return
        self._stop_event.clear()
        self.thread = threading.Thread(target=self.print_all_data, daemon=True)
        self.thread.start()

    def stop_print_loop(self):
        self._stop_event.set()
        if getattr(self, "thread", None):
            self.thread.join(timeout=1.0)

if __name__ == "__main__":
    t = Tactile()
    while True:
        t.print_sensor_data()