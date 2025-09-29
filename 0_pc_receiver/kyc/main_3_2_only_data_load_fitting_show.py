import os, sys
# import numpy as np
sys.path.append(os.getcwd())
from Tactile.tactile import Tactile
from SaveLoad.save import Save
from SaveLoad.load import Load
from Visualizer.matplot import Graph
from Visualizer.pres_temp import SensorBrowser
from Fitting.least_square import fit_all_sensors, plot_overlay_all, plot_grid

# np.set_printoptions(linewidth=100000, threshold=np.inf)
if __name__ == "__main__":
    '''Fitting'''
    # # fn="timestamp_data_250925_160345_t(41962,)P(41962, 21)T(41962, 21)KTrue"
    # # fn="timestamp_data_250926_094146_t(66499,)P(66499, 21)T(66499, 21)KTrue"
    # # fn="timestamp_data_250926_132828_t(39828,)P(39828, 21)T(39828, 21)KTrue"
    fn="timestamp_data_250926_144317_t(83977,)P(83977, 21)T(83977, 21)KTrue"
    l = Load(fn)
    time = l.data["tactile_time"]
    # pres = l.data["tactile_pres"]
    # temp = l.data["tactile_temp"]
    pres = l.data["tactile_pres_kf"]
    temp = l.data["tactile_temp_kf"]

    results, slopes, biases, r2s, counts = fit_all_sensors(temp, pres)
    
    ## s_lstsq = Save(tactile=None)
    ## s_lstsq.save_lstsq(slopes, biases, fn)

    # 간단히 화면에 확인
    for j in range(pres.shape[1]):
        print(f"Ch{j+1:02d}  a={slopes[j]:.4f}  b={biases[j]:9.3f}  R2={r2s[j]:.4f}  n={counts[j]}")

    # browser = SensorBrowser(time, pres, temp, layout=(3, 7), title="21 Sensors")
    # browser.show(mode="scatter", ms=0.5, alpha=0.3)
    
    # 1번 창: 오버레이 보기(빠른 트렌드)
    plot_overlay_all(temp, pres, slopes, biases, sample_every=3, dot_size=0.5)

    # 2번 창: 3x7 그리드(21채널) 상세 보기
    plot_grid(temp, pres, slopes, biases, layout=(3,7), dot_size=0.01)