import os, sys
# import numpy as np
sys.path.append(os.getcwd())
from Tactile.tactile import Tactile
from SaveLoad.save import Save
from SaveLoad.load import Load
from Visualizer.matplot import Graph
from Visualizer.pres_temp import SensorBrowser

# np.set_printoptions(linewidth=100000, threshold=np.inf)
if __name__ == "__main__":
    t = Tactile(port='COM12', baudrate=1_000_000, print_en=True)
    s = Save(tactile=t)
    g = Graph(t, auto_start = True)
# 노이즈제거
    fn = s.save()
    # fn="timestamp_data_250925_160345_t(41962,)P(41962, 21)T(41962, 21)KTrue"
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
    browser.show(mode="scatter", ms=6, alpha=0.3)
#Fitting