import os, sys
# import numpy as np
sys.path.append(os.getcwd())
from Tactile import Tactile, SaveTactile, LoadTactile, Graph, SensorBrowser, lstsq_plot_overlay_all, lstsq_plot_grid, lstsq_fit_all_sensors

# np.set_printoptions(linewidth=100000, threshold=np.inf)
if __name__ == "__main__":
    '''데이터 확인'''
    # fn="timestamp_data_250925_160345_t(41962,)P(41962, 21)T(41962, 21)KTrue"
    # fn="timestamp_data_250926_144317_t(83977,)P(83977, 21)T(83977, 21)KTrue"
    # fn="timestamp_data_251001_150712_t(47222,)P(47222, 21)T(47222, 21)KTrue"
    # fn="timestamp_data_251014_105855_t(10297,)P(10297, 21)T(10297, 21)KTrue"
    # fn="timestamp_data_251013_190015_t(24898,)P(24898, 21)T(24898, 21)KTrue_zero"
    # fn="timestamp_data_251013_200029_t(66443,)P(66443, 21)T(66443, 21)KTrue_2"

    # fn="timestamp_data_251015_103100_t(320,)P(320, 21)T(320, 21)KTrue"
    # fn="timestamp_data_251015_103341_t(29956,)P(29956, 21)T(29956, 21)KTrue"
    # fn="timestamp_data_251015_104544_t(19195,)P(19195, 21)T(19195, 21)KTrue"
    # fn="timestamp_data_251015_105547_t(17924,)P(17924, 21)T(17924, 21)KTrue"
    # fn="timestamp_data_251015_111016_t(36838,)P(36838, 21)T(36838, 21)KTrue"
    # fn="timestamp_data_251015_112214_t(33221,)P(33221, 21)T(33221, 21)KTrue"
    fn="timestamp_data_251015_105547_t(17924,)P(17924, 21)T(17924, 21)KTrue_5-6o"
    fn="timestamp_data_251015_112214_t(33221,)P(33221, 21)T(33221, 21)KTrue_6-6o"
    l = LoadTactile(fn)
    time = l.data["tactile_time"]
    # pres = l.data["tactile_pres"]
    # temp = l.data["tactile_temp"]
    pres = l.data["tactile_pres_kf"]
    temp = l.data["tactile_temp_kf"]
    # pres = l.data["tactile_pres_rts"]
    # temp = l.data["tactile_temp_rts"]

    # plot_pres_temp_grid(time, pres, temp)
    # 좀 기다려야 됨
    print(time)
    browser = SensorBrowser(time, pres, temp, layout=(3, 7), title="21 Sensors")
    browser.show(mode="scatter", ms=0.5, alpha=0.3)