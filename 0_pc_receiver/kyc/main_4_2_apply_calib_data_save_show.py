import os, sys
# import numpy as np
sys.path.append(os.getcwd())
from Tactile import Tactile, SaveTactile, LoadTactile, Graph, SensorBrowser, lstsq_plot_overlay_all, lstsq_plot_grid, lstsq_fit_all_sensors

if __name__ == "__main__":
    '''offset 실시간 적용 테스트'''
    fn_calib = "least_square_data_250926_152654"
    l_calib = LoadTactile(fn_calib, is_coefficients=True)
    l_calib.print_data("ls_a")
    l_calib.print_data("ls_b")

    calib_data = l_calib.data
    # print(f"{calib_data["ls_a"].shape}, {calib_data["ls_b"].shape}")
    t = Tactile(port='COM15', baudrate=1_000_000, print_en=False, calib_data=calib_data)
    s = SaveTactile(tactile=t)
    g = Graph(t, auto_start = True)
    fn = s.save_calib()

    l = LoadTactile(fn)
    time = l.data["tactile_time"]
    pres = l.data["tactile_pres"]
    temp = l.data["tactile_temp"]

    # plot_pres_temp_grid(time, pres, temp)
    browser = SensorBrowser(time, pres, temp, layout=(3, 7), title="21 Sensors")
    browser.show(mode="scatter", ms=1, alpha=0.3)