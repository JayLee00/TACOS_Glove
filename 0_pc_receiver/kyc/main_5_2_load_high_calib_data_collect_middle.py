import os, sys
# import numpy as np
# import matplotlib.pyplot as plt
sys.path.append(os.getcwd())
from Tactile import Tactile, SaveTactile, LoadTactile, Graph, SensorBrowser, lstsq_plot_overlay_all, lstsq_plot_grid, lstsq_fit_all_sensors

import numpy as np
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt

def plot_grid_lines(slopes, biases, layout=(3,7), xlim=(20.0, 40.0), ylim=None,
                    n_points=100, line_width=2.5,
                    title="Temp vs Pres (LS lines per sensor)"):
    """
    각 센서를 격자(기본 3x7)로 배치해 '기울기(slope)'와 '절편(bias)'만으로
    1차함수 y = a*x + b 형태의 직선을 그린다.

    Parameters
    ----------
    slopes : array-like, shape (N,)
        각 센서의 1차 회귀 기울기 a_k.
    biases : array-like, shape (N,)
        각 센서의 1차 회귀 절편 b_k.
    layout : tuple(int,int), default (3,7)
        (rows, cols) 서브플롯 배치.
    xlim : tuple(float,float), default (20.0, 40.0)
        온도 축 범위 [x_min, x_max].
    ylim : tuple(float,float) or None, default None
        압력 축 범위 [y_min, y_max]. None이면 자동 스케일.
    n_points : int, default 100
        직선 그릴 때의 x 샘플 개수.
    line_width : float, default 2.5
        직선 두께.
    title : str
        전체 figure 제목.
    """
    slopes = np.asarray(slopes, dtype=float)
    biases = np.asarray(biases, dtype=float)
    assert slopes.shape == biases.shape, "slopes와 biases의 길이가 같아야 합니다."

    N = slopes.size
    rows, cols = layout
    assert rows * cols >= N, "layout 칸수보다 센서 수가 많습니다."

    x_min, x_max = float(xlim[0]), float(xlim[1])
    assert x_max > x_min, "xlim은 (min, max) 형태여야 합니다."
    xx = np.linspace(x_min, x_max, n_points)

    # ylim 유효성 검사 (지정된 경우)
    if ylim is not None:
        y_min, y_max = float(ylim[0]), float(ylim[1])
        assert y_max > y_min, "ylim은 (min, max) 형태여야 합니다."

    fig, axes = plt.subplots(rows, cols, figsize=(cols*3.1, rows*2.7), squeeze=False)

    k = 0
    for r in range(rows):
        for c in range(cols):
            ax = axes[r, c]
            if k < N:
                a = slopes[k]; b = biases[k]
                if np.isfinite(a) and np.isfinite(b):
                    yy = a * xx + b
                    ax.plot(xx, yy, linewidth=line_width, color='black')
                else:
                    ax.text(0.5, 0.5, "N/A", ha='center', va='center', transform=ax.transAxes)

                ax.set_title(f"Sensor {k+1}")
                ax.set_xlabel("temperature [ºC]")
                ax.set_ylabel("pressure [hPa]")
                ax.set_xlim(x_min, x_max)
                if ylim is not None:
                    ax.set_ylim(y_min, y_max)
                ax.grid(True, linestyle="--", alpha=0.4)
            else:
                ax.axis("off")
            k += 1

    fig.suptitle(title)
    plt.tight_layout()
    plt.show()

import numpy as np
import matplotlib.pyplot as plt

def plot_grid_lines_dual(slopes_l, biases_l, slopes_h, biases_h,
                         layout=(3,7), xlim=(20.0, 40.0), ylim=None,
                         n_points=100, line_width=2.2,
                         pair_label=("L","H"), show_legend=True,
                         title="Temp vs Pres (Two LS lines per sensor)"):
    """
    각 센서 칸에 두 개의 1차함수 직선(y=a*x+b)을 겹쳐서 표시.

    Parameters
    ----------
    slopes_l, biases_l : array-like, shape (N,)
        첫 번째(line L) 계수들.
    slopes_h, biases_h : array-like, shape (N,)
        두 번째(line H) 계수들.
    layout : (rows, cols)
        서브플롯 배치.
    xlim : (xmin, xmax)
        온도축 범위.
    ylim : (ymin, ymax) or None
        압력축 범위. None이면 두 직선의 예측값으로부터 자동 계산(약간의 패딩 포함).
    n_points : int
        직선 샘플 개수.
    line_width : float
        선 두께.
    pair_label : (str, str)
        두 직선의 범례 라벨.
    show_legend : bool
        각 서브플롯에 범례 표시 여부.
    title : str
        전체 figure 제목.
    """
    # 배열화 및 길이 체크
    slopes_l = np.asarray(slopes_l, dtype=float)
    biases_l = np.asarray(biases_l, dtype=float)
    slopes_h = np.asarray(slopes_h, dtype=float)
    biases_h = np.asarray(biases_h, dtype=float)

    assert slopes_l.shape == biases_l.shape == slopes_h.shape == biases_h.shape, \
        "모든 계수 배열의 길이가 동일해야 합니다."

    N = slopes_l.size
    rows, cols = layout
    assert rows * cols >= N, "layout 칸수보다 센서 수가 많습니다."

    # x 샘플
    x_min, x_max = float(xlim[0]), float(xlim[1])
    assert x_max > x_min, "xlim은 (min, max) 형태여야 합니다."
    xx = np.linspace(x_min, x_max, n_points)

    # ylim 유효성 검사/자동계산 준비
    if ylim is not None:
        y_min, y_max = float(ylim[0]), float(ylim[1])
        assert y_max > y_min, "ylim은 (min, max) 형태여야 합니다."

    fig, axes = plt.subplots(rows, cols, figsize=(cols*3.1, rows*2.7), squeeze=False)

    k = 0
    for r in range(rows):
        for c in range(cols):
            ax = axes[r, c]
            if k < N:
                lines = []
                labels = []

                # 첫 번째 직선
                a1, b1 = slopes_l[k], biases_l[k]
                if np.isfinite(a1) and np.isfinite(b1):
                    yy1 = a1 * xx + b1
                    l1, = ax.plot(xx, yy1, linewidth=line_width, label=pair_label[0])
                    lines.append(l1); labels.append(pair_label[0])
                else:
                    ax.text(0.5, 0.65, "L:N/A", ha='center', va='center', transform=ax.transAxes)

                # 두 번째 직선
                a2, b2 = slopes_h[k], biases_h[k]
                if np.isfinite(a2) and np.isfinite(b2):
                    yy2 = a2 * xx + b2
                    # linestyle로 구분(색 지정을 피하려면 서로 다른 linestyle 권장)
                    l2, = ax.plot(xx, yy2, linewidth=line_width, linestyle="--", label=pair_label[1])
                    lines.append(l2); labels.append(pair_label[1])
                else:
                    ax.text(0.5, 0.35, "H:N/A", ha='center', va='center', transform=ax.transAxes)

                # 축/제목/그리드
                ax.set_title(f"Sensor {k+1}")
                ax.set_xlabel("temperature [ºC]")
                ax.set_ylabel("pressure [hPa]")
                ax.set_xlim(x_min, x_max)
                ax.grid(True, linestyle="--", alpha=0.4)

                # y축 범위: 지정 없으면 두 직선의 예측값에서 자동 패딩
                if ylim is not None:
                    ax.set_ylim(y_min, y_max)
                else:
                    # 현재 축의 데이터로부터 자동 계산 (있으면) + 소폭 패딩
                    ydata = []
                    if np.isfinite(a1) and np.isfinite(b1):
                        ydata.append(a1 * np.array([x_min, x_max]) + b1)
                    if np.isfinite(a2) and np.isfinite(b2):
                        ydata.append(a2 * np.array([x_min, x_max]) + b2)
                    if ydata:
                        ycat = np.concatenate(ydata)
                        ymin_auto, ymax_auto = np.min(ycat), np.max(ycat)
                        if np.isfinite(ymin_auto) and np.isfinite(ymax_auto) and ymax_auto > ymin_auto:
                            pad = 0.05 * (ymax_auto - ymin_auto)
                            ax.set_ylim(ymin_auto - pad, ymax_auto + pad)

                if show_legend and len(lines) >= 1:
                    ax.legend(frameon=False, loc="best")

            else:
                ax.axis("off")
            k += 1

    fig.suptitle(title)
    plt.tight_layout()
    plt.show()

def plot_grid_lines_triple(slopes_l, biases_l,
                           slopes_m, biases_m,
                           slopes_h, biases_h,
                           layout=(3,7), xlim=(20.0, 40.0), ylim=None,
                           n_points=100, line_width=2.2,
                           labels=("Low","Mid","High"), show_legend=True,
                           line_colors=("tab:blue","tab:green","tab:orange"),
                           title="Temp vs Pres (Three LS lines per sensor)"):
    """
    각 센서 칸에 3개의 1차함수 직선(y = a*x + b)을 겹쳐서 표시.
    a(기울기)나 b(절편)가 None/NaN/inf이면 해당 선은 표시하지 않음.

    colors: Low=파랑(tab:blue), Mid=초록(tab:green), High=주황(tab:orange)
    """

    # 배열화 (None 허용)
    slopes_l = np.asarray(slopes_l, dtype=object)
    biases_l = np.asarray(biases_l, dtype=object)
    slopes_m = np.asarray(slopes_m, dtype=object)
    biases_m = np.asarray(biases_m, dtype=object)
    slopes_h = np.asarray(slopes_h, dtype=object)
    biases_h = np.asarray(biases_h, dtype=object)

    # 길이 체크
    assert slopes_l.shape == biases_l.shape == slopes_m.shape == biases_m.shape == slopes_h.shape == biases_h.shape, \
        "모든 계수 배열의 길이가 동일해야 합니다."

    N = slopes_l.size
    rows, cols = layout
    assert rows * cols >= N, "layout 칸수보다 센서 수가 많습니다."

    # x 샘플
    x_min, x_max = float(xlim[0]), float(xlim[1])
    assert x_max > x_min, "xlim은 (min, max) 형태여야 합니다."
    xx = np.linspace(x_min, x_max, n_points)

    # ylim 유효성 검사
    if ylim is not None:
        y_min, y_max = float(ylim[0]), float(ylim[1])
        assert y_max > y_min, "ylim은 (min, max) 형태여야 합니다."

    fig, axes = plt.subplots(rows, cols, figsize=(cols*3.1, rows*2.7), squeeze=False)

    # 고정 색/스타일
    linestyles = ["-", "--", ":"]
    colors = list(line_colors)  # ("tab:blue","tab:green","tab:orange")
    arrs = [
        (slopes_l, biases_l, labels[0], linestyles[0], colors[0]),  # Low: blue
        (slopes_m, biases_m, labels[1], linestyles[1], colors[1]),  # Mid: green
        (slopes_h, biases_h, labels[2], linestyles[2], colors[2]),  # High: orange
    ]

    def _is_valid(a, b):
        if a is None or b is None:
            return False
        try:
            af = float(a); bf = float(b)
            return np.isfinite(af) and np.isfinite(bf)
        except (TypeError, ValueError):
            return False

    k = 0
    for r in range(rows):
        for c in range(cols):
            ax = axes[r, c]
            if k < N:
                plotted = False
                y_collect = []

                for (s_arr, b_arr, lab, ls, color) in arrs:
                    a = s_arr[k]; b = b_arr[k]
                    if _is_valid(a, b):
                        a = float(a); b = float(b)
                        yy = a * xx + b
                        ax.plot(xx, yy, linewidth=line_width, linestyle=ls, label=lab, color=color)
                        y_collect.append([a * x_min + b, a * x_max + b])
                        plotted = True

                ax.set_title(f"Sensor {k+1}")
                ax.set_xlabel("temperature [ºC]")
                ax.set_ylabel("pressure [hPa]")
                ax.set_xlim(x_min, x_max)
                ax.grid(True, linestyle="--", alpha=0.4)

                if ylim is not None:
                    ax.set_ylim(y_min, y_max)
                else:
                    if y_collect:
                        ycat = np.array(y_collect).ravel()
                        ymin_auto, ymax_auto = np.min(ycat), np.max(ycat)
                        if np.isfinite(ymin_auto) and np.isfinite(ymax_auto) and ymax_auto > ymin_auto:
                            pad = 0.05 * (ymax_auto - ymin_auto)
                            ax.set_ylim(ymin_auto - pad, ymax_auto + pad)

                if show_legend and plotted:
                    ax.legend(frameon=False, loc="best")
                if not plotted:
                    ax.text(0.5, 0.5, "N/A", ha='center', va='center', transform=ax.transAxes)
            else:
                ax.axis("off")
            k += 1

    fig.suptitle(title)
    plt.tight_layout()
    plt.show()



if __name__ == "__main__":
    fn_calib_1   = "least_square_data_251014_111950_from(timestamp_data_251013_191459_t(82320,)P(82320, 21)T(82320, 21)KTrue_1)"
    fn_calib_2   = "least_square_data_251014_112058_from(timestamp_data_251013_200029_t(66443,)P(66443, 21)T(66443, 21)KTrue_2)"
    fn_calib_3_1 = "least_square_data_251014_112140_from(timestamp_data_251014_110536_t(8984,)P(8984, 21)T(8984, 21)KTrue_3_1)"
    fn_calib_3_2 = "least_square_data_251014_112232_from(timestamp_data_251014_105855_t(10297,)P(10297, 21)T(10297, 21)KTrue_3_2)"
    fn_calib_3_3 = "least_square_data_251014_112314_from(timestamp_data_251014_110908_t(5932,)P(5932, 21)T(5932, 21)KTrue_3_3)"
    fn_calib_4   = "least_square_data_251014_112348_from(timestamp_data_251014_103939_t(37563,)P(37563, 21)T(37563, 21)KTrue_4)"
    fn_calib_5   = "least_square_data_251014_112423_from(timestamp_data_251014_100325_t(29368,)P(29368, 21)T(29368, 21)KTrue_5)"
    fn_calib_6   = "least_square_data_251014_112453_from(timestamp_data_251013_202420_t(66348,)P(66348, 21)T(66348, 21)KTrue_6)"
    fn_calib_7   = "least_square_data_251014_112526_from(timestamp_data_251014_101615_t(33228,)P(33228, 21)T(33228, 21)KTrue_7)"
    l_calib = [None]*21
    l_calib[0]    = LoadTactile(fn_calib_1  , is_coefficients=False)
    l_calib[1]    = LoadTactile(fn_calib_2  , is_coefficients=False)
    l_calib[2]    = None
    l_calib_2_1  = LoadTactile(fn_calib_3_1, is_coefficients=False)
    l_calib_2_2  = LoadTactile(fn_calib_3_2, is_coefficients=False)
    l_calib_2_3  = LoadTactile(fn_calib_3_3, is_coefficients=False)
    l_calib[3]    = LoadTactile(fn_calib_4  , is_coefficients=False)
    l_calib[4]    = LoadTactile(fn_calib_5  , is_coefficients=False)
    l_calib[5]    = LoadTactile(fn_calib_6  , is_coefficients=False)
    l_calib[6]    = LoadTactile(fn_calib_7  , is_coefficients=False)

    # calib_1_data    = l_calib_1  .data["ls_a"]
    # calib_2_data    = l_calib_2  .data["ls_a"]
    # calib_3_1_data  = l_calib_3_1.data["ls_a"]
    # calib_3_2_data  = l_calib_3_2.data["ls_a"]
    # calib_3_3_data  = l_calib_3_3.data["ls_a"]
    # calib_4_data    = l_calib_4  .data["ls_a"]
    # calib_5_data    = l_calib_5  .data["ls_a"]
    # calib_6_data    = l_calib_6  .data["ls_a"]
    # calib_7_data    = l_calib_7  .data["ls_a"]
    
    calib_data_a  = np.full(21, np.nan, dtype=float)
    calib_data_b  = np.full(21, np.nan, dtype=float)
    for i in range(7):
        if i == 2:
            continue
        for j in (0, 7, 14):
            calib_data_a[i+j], calib_data_b[i+j] = (l_calib[i].data["ls_a"][i+j], l_calib[i].data["ls_b"][i+j])
    
    calib_data_a[ 2], calib_data_b[ 2] = (l_calib_2_1.data["ls_a"][ 2], l_calib_2_1.data["ls_b"][ 2])
    calib_data_a[ 9], calib_data_b[ 9] = (l_calib_2_2.data["ls_a"][ 9], l_calib_2_2.data["ls_b"][ 9])
    calib_data_a[16], calib_data_b[16] = (l_calib_2_3.data["ls_a"][16], l_calib_2_3.data["ls_b"][16])

    print(calib_data_a)
    print(calib_data_b)

    fn_calib_low   = "least_square_data_251001_171337_4-6"
    l_calib_low    = LoadTactile(fn_calib_low  , is_coefficients=True)

    # plot_grid_lines(calib_data_a, calib_data_b, layout=(3,7), xlim=(28, 35), ylim=(2075, 2275))
    plot_grid_lines_dual(l_calib_low.data["ls_a"], l_calib_low.data["ls_b"], calib_data_a, calib_data_b, layout=(3,7), xlim=(25, 40), ylim=(1000, 2275))

    fn_calib_mid_4_6   = "least_square_data_251015_142056_from(timestamp_data_251015_104544_t(19195,)P(19195, 21)T(19195, 21)KTrue_4-6o)"
    fn_calib_mid_5_6   = "least_square_data_251015_142000_from(timestamp_data_251015_105547_t(17924,)P(17924, 21)T(17924, 21)KTrue_5-6o)"
    fn_calib_mid_6_6   = "least_square_data_251015_142454_from(timestamp_data_251015_112214_t(33221,)P(33221, 21)T(33221, 21)KTrue_6-6o)"
    l_calib_mid_4_6  = LoadTactile(fn_calib_mid_4_6  , is_coefficients=False)
    l_calib_mid_5_6  = LoadTactile(fn_calib_mid_5_6  , is_coefficients=False)
    l_calib_mid_6_6  = LoadTactile(fn_calib_mid_6_6  , is_coefficients=False)

    calib_mid_4_6_data = l_calib_mid_4_6.data
    calib_mid_5_6_data = l_calib_mid_5_6.data
    calib_mid_6_6_data = l_calib_mid_6_6.data

    calib_mid_data_a  = np.full(21, np.nan, dtype=float)
    calib_mid_data_b  = np.full(21, np.nan, dtype=float)

    calib_mid_data_a[5   ] = calib_mid_4_6_data["ls_a"][5   ]
    calib_mid_data_a[5+ 7] = calib_mid_5_6_data["ls_a"][5+ 7]
    calib_mid_data_a[5+14] = calib_mid_6_6_data["ls_a"][5+14]
    calib_mid_data_b[5   ] = calib_mid_4_6_data["ls_b"][5   ]
    calib_mid_data_b[5+ 7] = calib_mid_5_6_data["ls_b"][5+ 7]
    calib_mid_data_b[5+14] = calib_mid_6_6_data["ls_b"][5+14]

    plot_grid_lines_triple(l_calib_low.data["ls_a"], l_calib_low.data["ls_b"], calib_mid_data_a, calib_mid_data_b, calib_data_a, calib_data_b, layout=(3,7), xlim=(25, 40), ylim=(1000, 2275))
    while True:
        pass

