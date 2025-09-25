import os
import time
import numpy as np

from Tactile.tactile import Tactile
from Filter.kalman import TactileKalmanBatch

class Save:
    def __init__(self, tactile:Tactile, kalman_en = True):
        self.tactile = tactile
        self.kalman_en = kalman_en

        self.is_running = False
        self.tactile_time = None
        self.tactile_pres = None
        self.tactile_temp = None

        self.tactile_pres_kf  = None
        self.tactile_temp_kf  = None
        self.tactile_pres_rts = None
        self.tactile_temp_rts = None

        self.START_TIME = time.time()

        self.fn = ""

    def start(self):
        self.tactile.t_ser.save_enable = True
        self.is_running = True

    def stop(self):
        self.tactile.t_ser.save_enable = False
        self.is_running = False

    def get_all_poses(self):
        if self.is_running == True:
            self.stop()
            
        self.tactile_time = np.array(self.tactile.t_ser.timestamp,    dtype=np.float64)
        self.tactile_pres = np.array(self.tactile.t_ser.pressures,    dtype=np.float64)
        self.tactile_temp = np.array(self.tactile.t_ser.temperatures, dtype=np.float64)

        if self.kalman_en == True:
            try:
                kf = TactileKalmanBatch(
                    num_sensors=21,
                    # 필요시 시작값 튜닝 가능:
                    q_pres=(2e-4)**2, r_pres=(2e-3)**2,
                    q_temp=(5e-3)**2, r_temp=(5e-2)**2,
                    P0_pres=1.0, P0_temp=1.0
                )
                out = kf.fit(
                    ts=  self.tactile_time,
                    pres=self.tactile_pres,
                    temp=self.tactile_temp,
                    do_smooth=True,          # RTS 활성화
                    auto_noise=False,        # True로 두면 초반 window로 R/Q 자동추정
                    auto_win_seconds=1.0,
                    hz_hint=90.0,
                    q_from_r_ratio=0.01
                )
                self.tactile_pres_kf  = kf.results["pres_kf"]
                self.tactile_temp_kf  = kf.results["temp_kf"]
                self.tactile_pres_rts = kf.results["pres_rts"]
                self.tactile_temp_rts = kf.results["temp_rts"]
            except:
                self.kalman_en = False

    def save(self, filename = "timestamp_data"):#묵시적
        self.get_all_poses()

        lt = time.localtime(self.START_TIME)
        lt = time.strftime("%y%m%d_%H%M%S",lt)
        path = f"{os.getcwd()}/0_pc_receiver/kyc/SAVEFILES/{filename}_{lt}_t{self.tactile_time.shape}P{self.tactile_pres.shape}T{self.tactile_temp.shape}K{self.kalman_en}.npz"
        self.fn = f"{filename}_{lt}_t{self.tactile_time.shape}P{self.tactile_pres.shape}T{self.tactile_temp.shape}K{self.kalman_en}"
        if self.kalman_en == True:
            np.savez(f"{path}", 
                        tactile_time=self.tactile_time, 
                        tactile_pres=self.tactile_pres, 
                        tactile_temp=self.tactile_temp,
                        tactile_pres_kf =self.tactile_pres_kf ,
                        tactile_temp_kf =self.tactile_temp_kf ,
                        tactile_pres_rts=self.tactile_pres_rts,
                        tactile_temp_rts=self.tactile_temp_rts
                    )
            print(f"Saved {path}:", 
                    self.tactile_time.shape, 
                    self.tactile_pres.shape, 
                    self.tactile_temp.shape,
                    self.tactile_pres_kf .shape,
                    self.tactile_temp_kf .shape,
                    self.tactile_pres_rts.shape,
                    self.tactile_temp_rts.shape,
                )
        else:
            np.savez(f"{path}", 
                        tactile_time=self.tactile_time, 
                        tactile_pres=self.tactile_pres, 
                        tactile_temp=self.tactile_temp
                    )
            print(f"Saved {path}:", 
                    self.tactile_time.shape, 
                    self.tactile_pres.shape, 
                    self.tactile_temp.shape
                )
            
        return self.fn
        
    def __del__(self):
        pass