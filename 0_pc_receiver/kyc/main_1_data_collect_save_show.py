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
    '''데이터 수집'''
    t = Tactile(port='COM12', baudrate=1_000_000, print_en=True)
    s = Save(tactile=t)
    g = Graph(t, auto_start = True)
    '''save+노이즈제거'''
    fn = s.save()
    '''데이터 확인'''
    # fn="timestamp_data_250925_160345_t(41962,)P(41962, 21)T(41962, 21)KTrue"
    # fn="timestamp_data_250926_144317_t(83977,)P(83977, 21)T(83977, 21)KTrue"
    l = Load(fn)
    time = l.data["tactile_time"]
    # pres = l.data["tactile_pres"]
    # temp = l.data["tactile_temp"]
    pres = l.data["tactile_pres_kf"]
    temp = l.data["tactile_temp_kf"]
    # pres = l.data["tactile_pres_rts"]
    # temp = l.data["tactile_temp_rts"]

    # plot_pres_temp_grid(time, pres, temp)
    browser = SensorBrowser(time, pres, temp, layout=(3, 7), title="21 Sensors")
    browser.show(mode="scatter", ms=0.5, alpha=0.3)