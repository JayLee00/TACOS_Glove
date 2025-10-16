# import numpy as np
# import matplotlib.pyplot as plt
# from math import ceil

# class SensorBrowser:
#     """
#     time: (T,) 1D numpy array
#     pres: (T, N) 2D numpy array
#     temp: (T, N) 2D numpy array
#     layout: (rows, cols) for overview grid (default 3x7 for N=21)
#     """
#     def __init__(self, time, pres, temp, layout=(3, 7), title="Pres & Temp Viewer"):
#         # ---- 입력 검증 및 정리 ----
#         self.time = np.asarray(time).ravel()
#         self.pres = np.asarray(pres)
#         self.temp = np.asarray(temp)

#         assert self.time.ndim == 1, "time은 1차원 배열이어야 합니다."
#         assert self.pres.ndim == 2 and self.temp.ndim == 2, "pres, temp는 2차원 배열이어야 합니다."
#         T, N = self.pres.shape
#         assert self.temp.shape == (T, N), "pres와 temp의 shape가 같아야 합니다."
#         assert len(self.time) == T, "time 길이와 pres/temp의 첫 번째 차원(T)이 같아야 합니다."

#         self.T, self.N = T, N
#         self.title = title

#         # 그리드 레이아웃 결정
#         if layout is None:
#             cols = min(7, self.N)  # 가로 최대 7
#             rows = ceil(self.N / cols)
#             self.layout = (rows, cols)
#         else:
#             self.layout = layout
#             assert layout[0] * layout[1] >= self.N, "서브플롯 개수가 센서 수보다 적습니다."

#         # 페이지 인덱스 (0=그리드, 1..N=센서)
#         self.page = 0

#         # Figure 생성 및 이벤트 바인딩
#         self.fig = plt.figure(figsize=(12, 7))
#         self.cid_key = self.fig.canvas.mpl_connect('key_press_event', self._on_key)

#         self._draw_page()  # 초기 화면

#     # ---------- 이벤트 핸들러 ----------
#     def _on_key(self, event):
#         if event.key in ('right',):
#             self._goto(self.page + 1)
#         elif event.key in ('left',):
#             self._goto(self.page - 1)
#         elif event.key in ('home',):
#             self._goto(0)
#         elif event.key in ('end',):
#             self._goto(self.N)  # 마지막 센서
#         elif event.key in ('g', 'G'):
#             self._goto(0)
#         elif event.key in ('escape', 'q', 'Q'):
#             plt.close(self.fig)

#     def _goto(self, new_page):
#         # 범위 래핑(원형 넘김)
#         if new_page < 0:
#             new_page = self.N
#         if new_page > self.N:
#             new_page = 0
#         self.page = new_page
#         self._draw_page()

#     # ---------- 페이지 렌더 ----------
#     def _draw_page(self):
#         self.fig.clf()
#         if self.page == 0:
#             self._draw_overview()
#             self.fig.suptitle(f"[0/ {self.N}] Overview (Grid) — {self.title}", y=0.98, fontsize=13)
#         else:
#             self._draw_sensor(self.page - 1)
#             self.fig.suptitle(f"[{self.page}/ {self.N}] Sensor {self.page} — {self.title}", y=0.98, fontsize=13)
#         self.fig.tight_layout(rect=[0, 0, 1, 0.95])
#         self.fig.canvas.draw_idle()

#     def _draw_overview(self):
#         rows, cols = self.layout
#         axes = self.fig.subplots(rows, cols, sharex=True)
#         axes = np.atleast_2d(axes).ravel()

#         # 전역 범례용 첫 라인 핸들
#         h_pres_first = None
#         h_temp_first = None

#         for i in range(rows * cols):
#             ax = axes[i]
#             if i < self.N:
#                 ax_r = ax.twinx()

#                 hp, = ax.  plot(self.time, self.pres[:, i], linewidth=1.0)
#                 ht, = ax_r.plot(self.time, self.temp[:, i], linewidth=1.0, linestyle='--', color='orange')

#                 if h_pres_first is None: h_pres_first = hp
#                 if h_temp_first is None: h_temp_first = ht

#                 ax.set_title(f"S{i+1}", fontsize=9)
#                 ax.grid(True, linestyle='--', alpha=0.3)

#                 col_idx = i % cols
#                 # 좌열/우열에만 y라벨
#                 if col_idx == 0:
#                     ax.set_ylabel("pres", fontsize=8)
#                 if col_idx == cols - 1:
#                     ax_r.set_ylabel("temp", fontsize=8)
#                 # x라벨은 마지막 행만
#                 if i // cols == rows - 1:
#                     ax.set_xlabel("time", fontsize=8)
                
#                 # ax.  set_ylim(1200, 2500)
#                 # ax_r.set_ylim(15, 36)

#             else:
#                 ax.set_visible(False)

#         if h_pres_first and h_temp_first:
#             self.fig.legend([h_pres_first, h_temp_first], ["pres (line)", "temp (line)"],
#                             loc="upper center", ncol=2, frameon=False, fontsize=10)

#     def _draw_sensor(self, sensor_idx: int):
#         ax = self.fig.add_subplot(111)
#         ax_r = ax.twinx()

#         # ax.  set_ylim(1200, 2500)
#         # ax_r.set_ylim(15, 36)

#         hp, = ax.  plot(self.time, self.pres[:, sensor_idx], marker='o', markersize=2, linewidth=0.5, label='pres')
#         ht, = ax_r.plot(self.time, self.temp[:, sensor_idx], marker='s', markersize=2, linewidth=0.5, label='temp', linestyle='--', color='orange')

#         ax.set_xlabel("time")
#         ax.set_ylabel("pres", rotation=0, labelpad=25, va='center')
#         ax_r.set_ylabel("temp", rotation=0, labelpad=25, va='center')

#         ax.grid(True, linestyle='--', alpha=0.35)
#         ax.set_title(f"Sensor {sensor_idx+1}")

#         # 범례
#         self.fig.legend([hp, ht], ["pres (line)", "temp (line)"], loc="upper right", frameon=False)

#     def _draw_temp_vs_pres_scatter(self, ms=9, alpha=0.35, by_sensor=False, color=None, title="Temp (x) vs Pres (y)"):
#         """
#         시간축은 무시하고, 모든 시점·모든 센서 데이터를 점으로 찍어
#         temp를 x축, pres를 y축으로 표시합니다.

#         ms: marker size (포인트)  -> 실제 scatter의 s는 pt^2이므로 s = ms**2로 변환
#         alpha: 투명도 (겹침 완화)
#         by_sensor: True면 센서별 색상 구분 (탐색용)
#         color: 단일 색상 지정 (by_sensor=False일 때만 사용)
#         """
#         ax = self.fig.add_subplot(111)

#         # (T, N) -> (T*N,)
#         x = self.temp.reshape(-1)
#         y = self.pres.reshape(-1)

#         if by_sensor:
#             # 각 점의 센서 인덱스 (0..N-1)를 색상값으로 사용
#             sensor_idx = np.repeat(np.arange(self.N), self.T)
#             sc = ax.scatter(x, y, s=ms**2, c=sensor_idx, cmap='tab20', alpha=alpha, edgecolors='none')
#             # 컬러바(선택): 센서 번호 확인용
#             cbar = self.fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
#             cbar.set_label("sensor id (0-based)")
#         else:
#             sc = ax.scatter(x, y, s=ms**2, alpha=alpha, edgecolors='none', color=(color or 'tab:blue'))

#         ax.set_xlabel("temp")
#         ax.set_ylabel("pres")
#         ax.grid(True, linestyle='--', alpha=0.35)
#         ax.set_title(title)
#     # ---------- 외부 호출 ----------
#     def show(self, mode="browser", **kwargs):
#         """
#         mode:
#         - "browser": 0번(그리드) + ←/→로 센서 넘기는 기존 뷰어
#         - "scatter": temp(x)-pres(y) 산점도(모든 데이터)
#         kwargs:
#         - scatter 모드에서 _draw_temp_vs_pres_scatter()의 인자 전달(ms, alpha, by_sensor, color, title)
#         """
#         if mode == "browser":
#             print("Keys: ←/→ to navigate, 'g' for grid, Home/End, 'q' or ESC to quit.")
#             plt.show()
#         elif mode == "scatter":
#             self.fig.clf()
#             self._draw_temp_vs_pres_scatter(**kwargs)
#             self.fig.tight_layout()
#             plt.show()
#         else:
#             raise ValueError("mode must be 'browser' or 'scatter'")

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
#             hp, = ax.  plot(time, pres[:, i], marker='o', linewidth=0.5)
#             ht, = ax_r.plot(time, temp[:, i], marker='s', linewidth=0.5, linestyle='--', color='orange')

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
# # ================= 사용 예시 =================
# if __name__ == "__main__":
#     # 가상 데이터 (실데이터로 교체해서 사용)
#     T = 200
#     N = 21
#     time = np.linspace(0, 10, T)
#     pres = 1200 + 30*np.sin(time[:, None] * (0.8 + 0.2*np.arange(1, N+1))) + 20*np.random.randn(T, N)
#     temp = 25 + 3*np.cos(time[:, None] * (0.6 + 0.1*np.arange(1, N+1))) + 0.5*np.random.randn(T, N)

#     browser = SensorBrowser(time, pres, temp, layout=(3, 7), title="21 Sensors")
#     browser.show()
