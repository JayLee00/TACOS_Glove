import os, sys
import numpy as np
import matplotlib.pyplot as plt
from math import ceil
sys.path.append(os.getcwd())

# from Visualizer.pres_temp import plot_pres_temp_grid

class LoadTactile:
    def __init__(self, filename, is_coefficients = False):
        # 이 파일(load.py)이 위치한 디렉토리의 상위 폴더('ljs')를 기준으로 경로를 설정합니다.
        # 이렇게 하면 스크립트를 어디서 실행하든 경로가 항상 일정하게 유지됩니다.
        ljs_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if is_coefficients == False:
            self.path = os.path.join(ljs_dir, "SAVEFILES", f"{filename}.npz")
        else:
            self.path = os.path.join(ljs_dir, "OFFSET_TABLE", f"{filename}.npz")

        self.data = None
        self.load()

    def load(self):
        self.data = np.load(f"{self.path}")

    def print_data(self, part = "actions"):
        data = self.data[part]
        print(data, data.shape, flush=True)

# def plot_pres_temp_grid(time, pres, temp, layout=(3, 7), title="21 Sensors: pres & temp vs time"):
#     """
#     time: (T,) 1D array
#     pres: (T, N) 2D array, N == 21 (기본 가정)
#     temp: (T, N) 2D array, same shape as pres
#     layout: (rows, cols) 서브플롯 배열. 21개 기본값은 (3, 7).
#     """
#     # --- 입력 정리/검증 ---
#     time = np.asarray(time).ravel()
#     pres = np.asarray(pres)
#     temp = np.asarray(temp)
#     assert time.ndim == 1, "time은 1차원 배열이어야 합니다."
#     assert pres.ndim == 2 and temp.ndim == 2, "pres, temp는 2차원 배열이어야 합니다."
#     T, N = pres.shape
#     assert temp.shape == (T, N), "pres, temp의 shape가 같아야 합니다."
#     assert len(time) == T, "time 길이와 pres/temp의 첫 번째 차원(T)이 같아야 합니다."

#     # --- 레이아웃 결정 (기본 3x7). 필요 시 자동 배치 주석 참고 ---
#     rows, cols = layout
#     assert rows * cols >= N, "서브플롯 개수가 센서 수보다 적습니다."

#     # --- Figure/Subplots ---
#     fig, axes = plt.subplots(rows, cols, figsize=(cols*3.6, rows*2.6), sharex=True)
#     axes = np.atleast_2d(axes)
#     axes_flat = axes.ravel()

#     # 전역 범례용 핸들
#     h_pres_first = None
#     h_temp_first = None

#     for i in range(rows * cols):
#         ax = axes_flat[i]
#         if i < N:
#             ax_r = ax.twinx()  # 우측 축

#             # 꺾은선: pres(좌), temp(우)
#             hp, = ax.plot(time, pres[:, i], marker='o', linewidth=0.5)
#             ht, = ax_r.plot(time, temp[:, i], marker='s', linewidth=0.5, linestyle='--')

#             if h_pres_first is None: h_pres_first = hp
#             if h_temp_first is None: h_temp_first = ht

#             # 타이틀/눈금/그리드
#             ax.set_title(f"Sensor {i+1}", fontsize=10)
#             ax.grid(True, linestyle='--', alpha=0.3)

#             # 좌/우 라벨은 가장 왼쪽/오른쪽 열에만 표시 (혼잡도 감소)
#             col_idx = i % cols
#             if col_idx == 0:
#                 ax.set_ylabel("pres")
#             else:
#                 ax.set_ylabel("")
#             if col_idx == cols - 1:
#                 ax_r.set_ylabel("temp")
#             else:
#                 ax_r.set_ylabel("")

#             # 필요 시 전 서브플롯에 라벨을 달고 싶다면 위 조건 제거

#         else:
#             # 빈 칸은 끄기
#             ax.set_visible(False)

#     # 공통 X 라벨(맨 아래 행만 보이지만 sharex=True로 충분)
#     for ax in axes[-1, :]:
#         ax.set_xlabel("time")

#     # 전역 범례
#     if h_pres_first and h_temp_first:
#         fig.legend([h_pres_first, h_temp_first], ["pres (line)", "temp (line)"],
#                    loc="upper center", ncol=2, frameon=False, fontsize=10)

#     fig.suptitle(title, y=0.98, fontsize=12)
#     plt.tight_layout(rect=[0, 0, 1, 0.95])  # 상단에 범례/제목 여유 공간
#     plt.show()

if __name__ == "__main__":
    np.set_printoptions(precision=7, suppress=False, linewidth=200, threshold=10**9)

    # test_handside = HandSide.BOTH
    # test = MoCAP_Manager(handsides=test_handside, use_trackers=True)
    # l = Load("timestamp_data_250829_154232")
    l = LoadTactile("timestamp_data_250925_094512_t(413,)P(413, 21)T(413, 21)")

    # l.print_data("tactile_time")
    # print("")
    # l.print_data("tactile_pres")
    # print("")
    l.print_data("tactile_temp")

    time = l.data["tactile_time"]
    pres = l.data["tactile_pres"]
    temp = l.data["tactile_temp"]

    # plot_pres_temp_grid(time, pres, temp)