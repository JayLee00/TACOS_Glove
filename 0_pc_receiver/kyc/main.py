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
#     t = Tactile(port='COM12', baudrate=1_000_000, print_en=True)
#     s = Save(tactile=t)
#     g = Graph(t, auto_start = True)
# # 노이즈제거
#     fn = s.save()
#     # fn="timestamp_data_250925_160345_t(41962,)P(41962, 21)T(41962, 21)KTrue"
#     l = Load(fn)
#     time = l.data["tactile_time"]
#     # pres = l.data["tactile_pres"]
#     # temp = l.data["tactile_temp"]
#     pres = l.data["tactile_pres_kf"]
#     temp = l.data["tactile_temp_kf"]
#     # pres = l.data["tactile_pres_rts"]
#     # temp = l.data["tactile_temp_rts"]

#     # plot_pres_temp_grid(time, pres, temp)
#     browser = SensorBrowser(time, pres, temp, layout=(3, 7), title="21 Sensors")
#     browser.show(mode="scatter", ms=6, alpha=0.3)
#Fitting
    # path = r"./tactile_session_rts.npz"   # <- 네 파일 경로로 교체
    fn="timestamp_data_250925_160345_t(41962,)P(41962, 21)T(41962, 21)KTrue"
    l = Load(fn)
    time = l.data["tactile_time"]
    # pres = l.data["tactile_pres"]
    # temp = l.data["tactile_temp"]
    pres = l.data["tactile_pres_kf"]
    temp = l.data["tactile_temp_kf"]

    results, slopes, biases, r2s, counts = fit_all_sensors(temp, pres)

    # 간단히 화면에 확인
    for j in range(pres.shape[1]):
        print(f"Ch{j:02d}  a={slopes[j]:.6g}  b={biases[j]:.6g}  R2={r2s[j]:.4f}  n={counts[j]}")

    # 오버레이 보기(빠른 트렌드)
    plot_overlay_all(temp, pres, slopes, biases, sample_every=3, dot_size=5)

    # 3x7 그리드(21채널) 상세 보기
    plot_grid(temp, pres, slopes, biases, layout=(3,7), dot_size=6)