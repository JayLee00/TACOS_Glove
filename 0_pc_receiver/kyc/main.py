import os, sys
# import numpy as np
sys.path.append(os.getcwd())
from Tactile import Tactile, SaveTactile, LoadTactile, Graph, SensorBrowser, lstsq_plot_overlay_all, lstsq_plot_grid, lstsq_fit_all_sensors

# np.set_printoptions(linewidth=100000, threshold=np.inf)
if __name__ == "__main__":
    '''데이터 수집'''
    # t = Tactile(port='COM12', baudrate=1_000_000, print_en=True)
    # s = Save(tactile=t)
    # g = Graph(t, auto_start = True)
    '''save+노이즈제거'''
#     fn = s.save()
# 데이터 확인
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

    '''Fitting'''
    # # fn="timestamp_data_250925_160345_t(41962,)P(41962, 21)T(41962, 21)KTrue"
    # # fn="timestamp_data_250926_094146_t(66499,)P(66499, 21)T(66499, 21)KTrue"
    # # fn="timestamp_data_250926_132828_t(39828,)P(39828, 21)T(39828, 21)KTrue"
    fn="timestamp_data_250926_144317_t(83977,)P(83977, 21)T(83977, 21)KTrue"
    l = LoadTactile(fn)
    time = l.data["tactile_time"]
    # pres = l.data["tactile_pres"]
    # temp = l.data["tactile_temp"]
    pres = l.data["tactile_pres_kf"]
    temp = l.data["tactile_temp_kf"]

    results, slopes, biases, r2s, counts = lstsq_fit_all_sensors(temp, pres)
    # s_lstsq = Save(tactile=None)
    # s_lstsq.save_lstsq(slopes, biases, fn)

    # # 간단히 화면에 확인
    for j in range(pres.shape[1]):
        print(f"Ch{j+1:02d}  a={slopes[j]:.6g}  b={biases[j]:.6g}  \tR2={r2s[j]:.4f}  n={counts[j]}")

    # # browser = SensorBrowser(time, pres, temp, layout=(3, 7), title="21 Sensors")
    # # browser.show(mode="scatter", ms=6, alpha=0.3)
    
    # # # 오버레이 보기(빠른 트렌드)
    # # plot_overlay_all(temp, pres, slopes, biases, sample_every=3, dot_size=5)

    # # 3x7 그리드(21채널) 상세 보기
    # plot_grid(temp, pres, slopes, biases, layout=(3,7), dot_size=0.1)

    '''offset 실시간 적용 테스트'''
    # fn_calib = "least_square_data_250926_152654"
    # l_calib = Load(fn_calib, is_coefficients=True)
    # # l_calib.print_data("ls_a")
    # # l_calib.print_data("ls_b")

    # calib_data = l_calib.data
    # # print(f"{calib_data["ls_a"].shape}, {calib_data["ls_b"].shape}")
    # t = Tactile(port='COM12', baudrate=1_000_000, print_en=True, calib_data=calib_data)
    # g = Graph(t, auto_start = True)