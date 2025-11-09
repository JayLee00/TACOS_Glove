import os, sys
# import numpy as np
sys.path.append(os.getcwd())
from Tactile import Tactile, SaveTactile, LoadTactile, Graph, SensorBrowser, lstsq_plot_overlay_all, lstsq_plot_grid, lstsq_fit_all_sensors

if __name__ == "__main__":
    '''offset 실시간 적용 테스트'''
    fn_calib = "least_square_data_250926_152654_1-3"
    # fn_calib = "least_square_data_251001_171337_4-6"
    l_calib = LoadTactile(fn_calib, is_coefficients=True)
    l_calib.print_data("ls_a")
    l_calib.print_data("ls_b")

    calib_data = l_calib.data
    # print(f"{calib_data["ls_a"].shape}, {calib_data["ls_b"].shape}")
    t = Tactile(port='COM16', baudrate=1_000_000, print_en=True, calib_data=calib_data)
    t.connect()
    g = Graph(t, auto_start = True)