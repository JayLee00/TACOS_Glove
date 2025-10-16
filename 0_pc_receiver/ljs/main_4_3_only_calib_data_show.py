import os, sys
# import numpy as np
sys.path.append(os.getcwd())
from Tactile import Tactile, SaveTactile, LoadTactile, Graph, SensorBrowser, lstsq_plot_overlay_all, lstsq_plot_grid, lstsq_fit_all_sensors

if __name__ == "__main__":
    fn = "timestamp_data_251001_104137_t(2876,)P(2876, 21)"

    l = LoadTactile(fn)
    time = l.data["tactile_time"]
    # pres = l.data["tactile_pres"]
    # temp = l.data["tactile_temp"]
    pres = l.data["tactile_pres"]
    temp = l.data["tactile_temp"]
    # pres = l.data["tactile_pres_rts"]
    # temp = l.data["tactile_temp_rts"]

    # plot_pres_temp_grid(time, pres, temp)
    browser = SensorBrowser(time, pres, temp, layout=(3, 7), title="21 Sensors")
    browser.show(mode="scatter", ms=1, alpha=0.3)