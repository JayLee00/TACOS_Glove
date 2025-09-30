import os, sys
# import numpy as np
sys.path.append(os.getcwd())
from Tactile.tactile import Tactile
from SaveLoad.save import Save
from SaveLoad.load import Load
from Visualizer.matplot import Graph
from Visualizer.pres_temp import SensorBrowser
from Visualizer.least_square import lstsq_plot_overlay_all, lstsq_plot_grid
from Fitting.least_square import lstsq_fit_all_sensors

if __name__ == "__main__":
    '''offset 실시간 적용 테스트'''
    fn_calib = "least_square_data_250926_152654"
    l_calib = Load(fn_calib, is_coefficients=True)
    l_calib.print_data("ls_a")
    l_calib.print_data("ls_b")

    calib_data = l_calib.data
    print(f"{calib_data["ls_a"].shape}, {calib_data["ls_b"].shape}")
    t = Tactile(port='COM12', baudrate=1_000_000, print_en=True, calib_data=calib_data)
    g = Graph(t, auto_start = True)