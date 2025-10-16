import os, sys
# import numpy as np
sys.path.append(os.getcwd())
from Tactile import Tactile, SaveTactile, LoadTactile, Graph, SensorBrowser, lstsq_plot_overlay_all, lstsq_plot_grid, lstsq_fit_all_sensors

# np.set_printoptions(linewidth=100000, threshold=np.inf)
if __name__ == "__main__":
    '''Fitting'''
    # # fn="timestamp_data_250925_160345_t(41962,)P(41962, 21)T(41962, 21)KTrue"
    # # fn="timestamp_data_250926_094146_t(66499,)P(66499, 21)T(66499, 21)KTrue"
    # # fn="timestamp_data_250926_132828_t(39828,)P(39828, 21)T(39828, 21)KTrue"
    # fn="timestamp_data_250926_144317_t(83977,)P(83977, 21)T(83977, 21)KTrue"
    # fn="timestamp_data_251001_165857_t(42946,)P(42946, 21)T(42946, 21)KTrue"

    # fn="timestamp_data_251013_190015_t(24898,)P(24898, 21)T(24898, 21)KTrue_zero"
    # fn="timestamp_data_251013_191459_t(82320,)P(82320, 21)T(82320, 21)KTrue_1"
    # fn="timestamp_data_251013_200029_t(66443,)P(66443, 21)T(66443, 21)KTrue_2"
    # fn="timestamp_data_251014_110536_t(8984,)P(8984, 21)T(8984, 21)KTrue_3_1"
    # fn="timestamp_data_251014_105855_t(10297,)P(10297, 21)T(10297, 21)KTrue_3_2"
    # fn="timestamp_data_251014_110908_t(5932,)P(5932, 21)T(5932, 21)KTrue_3_3"
    # fn="timestamp_data_251014_103939_t(37563,)P(37563, 21)T(37563, 21)KTrue_4"
    # fn="timestamp_data_251014_100325_t(29368,)P(29368, 21)T(29368, 21)KTrue_5"
    # fn="timestamp_data_251013_202420_t(66348,)P(66348, 21)T(66348, 21)KTrue_6"
    # fn="timestamp_data_251014_101615_t(33228,)P(33228, 21)T(33228, 21)KTrue_7"

    # fn="timestamp_data_251013_200029_t(66443,)P(66443, 21)T(66443, 21)KTrue_2"

    # fn="timestamp_data_251015_104544_t(19195,)P(19195, 21)T(19195, 21)KTrue_4-6o" # [1000:3000]
    # fn="timestamp_data_251015_105547_t(17924,)P(17924, 21)T(17924, 21)KTrue_5-6o"[:7500]
    fn="timestamp_data_251015_112214_t(33221,)P(33221, 21)T(33221, 21)KTrue_6-6o"
    l = LoadTactile(fn)
    time = l.data["tactile_time"]   [:8000]
    # pres = l.data["tactile_pres"] [:8000]
    # temp = l.data["tactile_temp"] [:8000]
    pres = l.data["tactile_pres_kf"][:8000]
    temp = l.data["tactile_temp_kf"][:8000]

    results, slopes, biases, r2s, counts = lstsq_fit_all_sensors(temp, pres)
    
    s_lstsq = SaveTactile(tactile=None)
    s_lstsq.save_lstsq(slopes, biases, fn)

    # 간단히 화면에 확인
    for j in range(pres.shape[1]):
        print(f"Ch{j+1:02d}  a={slopes[j]:.4f}  b={biases[j]:9.3f}  R2={r2s[j]:.4f}  n={counts[j]}")

    # browser = SensorBrowser(time, pres, temp, layout=(3, 7), title="21 Sensors")
    # browser.show(mode="scatter", ms=0.5, alpha=0.3)
    
    # 1번 창: 오버레이 보기(빠른 트렌드)
    lstsq_plot_overlay_all(temp, pres, slopes, biases, sample_every=3, dot_size=0.5)

    # 2번 창: 3x7 그리드(21채널) 상세 보기
    lstsq_plot_grid(temp, pres, slopes, biases, layout=(3,7), dot_size=0.01)