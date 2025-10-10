import os
import time
import numpy as np

from Tactile.tactile import Tactile
from Filter.kalman import TactileKalmanBatch

class SaveTactile:
    def __init__(self, tactile:Tactile, kalman_en = True, start_delay_sec = 0):
        self.tactile = tactile
        self.kalman_en = kalman_en
        self.start_delay_sec = start_delay_sec

        self.is_running = False
        self.tactile_time = None
        self.tactile_pres = None
        self.tactile_temp = None

        self.tactile_pres_kf  = None
        self.tactile_temp_kf  = None
        self.tactile_pres_rts = None
        self.tactile_temp_rts = None

        self.START_TIME = time.time()
        lt = time.localtime(self.START_TIME)
        self.lt = time.strftime("%y%m%d_%H%M%S",lt)

        self.filename = ""
        self.filename_lstsq = ""
        if self.tactile is not None:
            if self.start_delay_sec != 0:
                time.sleep(self.start_delay_sec)
            self.start()

    def start(self):
        self.tactile.t_ser.save_enable = True
        self.is_running = True

    def stop(self):
        self.tactile.t_ser.save_enable = False
        self.is_running = False

    def get_all_poses(self):
        if self.is_running == True:
            self.stop()
            
        self.tactile_time = np.array(self.tactile.t_ser.save_time,    dtype=np.float64)
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

        self.filename = f"{filename}_{self.lt}_t{self.tactile_time.shape}P{self.tactile_pres.shape}T{self.tactile_temp.shape}K{self.kalman_en}"
        path = f"{os.getcwd()}/0_pc_receiver/kyc/SAVEFILES/{self.filename}.npz"
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
            
        return self.filename
    
    def save_lstsq(self, a, b, file_explain = "least_square_data"):
        filename = "least_square_data"
        self.filename_lstsq = f"{filename}_{self.lt}_from({file_explain})"
        path = f"{os.getcwd()}/0_pc_receiver/kyc/SAVEFILES/{self.filename_lstsq}.npz"
        
        np.savez(f"{path}", 
                    ls_a=a, 
                    ls_b=b
                )
        print(f"Saved: {path}:", 
                a.shape, 
                b.shape
            )
            
        return self.filename_lstsq
        
    def get_all_poses_calib(self):
        if self.is_running == True:
            self.stop()
        # tactile
        self.tactile_time     = np.array(self.tactile.t_ser.save_time,    dtype=np.float64)
        self.tactile_pres_tmp = np.array(self.tactile.t_ser.save_data,    dtype=np.float64)
        self.tactile_temp_tmp = np.array(self.tactile.t_ser.temperatures, dtype=np.float64)
        self.tactile_shape =self.tactile_time.shape
        kf = TactileKalmanBatch(
            num_sensors=21,
            # 필요시 시작값 튜닝 가능:
            q_pres=(2e-4)**2, r_pres=(2e-3)**2,
            q_temp=(5e-3)**2, r_temp=(5e-2)**2,
            P0_pres=1.0, P0_temp=1.0
        )
        out = kf.fit(
            ts=  self.tactile_time,
            pres=self.tactile_pres_tmp,
            temp=self.tactile_temp_tmp,
            do_smooth=True,          # RTS 활성화
            auto_noise=False,        # True로 두면 초반 window로 R/Q 자동추정
            auto_win_seconds=1.0,
            hz_hint=90.0,
            q_from_r_ratio=0.01
        )
        self.tactile_pres_calib = kf.results["pres_kf"]
        self.tactile_temp_kf    = kf.results["temp_kf"]
        # self.tactile_left_pres.reshape(self.tactile_left_pres[0], 3, 7)

    def save_calib(self, filename_begin = "timestamp_data"):#묵시적
        self.get_all_poses_calib()

        filename = f"{filename_begin}_{self.lt}_t{self.tactile_time.shape}P{self.tactile_pres_calib.shape}T{self.tactile_temp_kf.shape}"
        path = f"{os.getcwd()}/0_pc_receiver/kyc/SAVEFILES/{filename}.npz"
        np.savez(f"{path}", 
                 tactile_time = self.tactile_time,
                 tactile_pres = self.tactile_pres_calib,
                 tactile_temp = self.tactile_temp_kf
                 )
        print(f"Saved {path}:",
                self.tactile_time      .shape, 
                self.tactile_pres_calib.shape,
                self.tactile_temp_kf.shape
              )
        return filename

    def __del__(self):
        pass