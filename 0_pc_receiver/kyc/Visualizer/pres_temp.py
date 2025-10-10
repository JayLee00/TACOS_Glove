import numpy as np
import matplotlib.pyplot as plt
from math import ceil
START_IDX = 0
END_IDX = -1
class SensorBrowser:
    """
    time: (T,) 1D numpy array
    pres: (T, N) 2D numpy array
    temp: (T, N) 2D numpy array
    layout: (rows, cols) for overview grid (default 3x7 for N=21)
    """
    def __init__(self, time, pres, temp, layout=(3, 7), title="Pres & Temp Viewer"):
        # ---- 입력 검증 및 정리 ----
        self.time = np.asarray(time).ravel()
        self.pres = np.asarray(pres)
        self.temp = np.asarray(temp)

        assert self.time.ndim == 1, "time은 1차원 배열이어야 합니다."
        assert self.pres.ndim == 2 and self.temp.ndim == 2, "pres, temp는 2차원 배열이어야 합니다."
        T, N = self.pres.shape
        assert self.temp.shape == (T, N), "pres와 temp의 shape가 같아야 합니다."
        assert len(self.time) == T, "time 길이와 pres/temp의 첫 번째 차원(T)이 같아야 합니다."

        self.T, self.N = T, N
        self.title = title

        # 그리드 레이아웃 결정
        if layout is None:
            cols = min(7, self.N)  # 가로 최대 7
            rows = ceil(self.N / cols)
            self.layout = (rows, cols)
        else:
            self.layout = layout
            assert layout[0] * layout[1] >= self.N, "서브플롯 개수가 센서 수보다 적습니다."

        # 페이지 인덱스 (0=그리드, 1..N=센서)
        self.page = 0

        # ----- 추가: 모드 & 산점도 기본 옵션 -----
        # mode: "browser"(시계열) | "scatter"(temp→pres 산점도)
        self.mode = "browser"
        self.scatter_ms = 1
        self.scatter_alpha = 0.5

        # Figure 생성 및 이벤트 바인딩
        self.fig = plt.figure(figsize=(12, 7))
        self.cid_key = self.fig.canvas.mpl_connect('key_press_event', self._on_key)

        self._draw_page()  # 초기 화면

    # ---------- 이벤트 핸들러 ----------
    def _on_key(self, event):
        if event.key in ('right',):
            self._goto(self.page + 1)
        elif event.key in ('left',):
            self._goto(self.page - 1)
        elif event.key in ('home',):
            self._goto(0)
        elif event.key in ('end',):
            self._goto(self.N)  # 마지막 센서
        elif event.key in ('g', 'G'):
            self._goto(0)
        elif event.key in ('m', 'M'):
            # 모드 토글
            self.mode = "scatter" if self.mode == "browser" else "browser"
            self._draw_page()
        elif event.key in ('escape', 'q', 'Q'):
            plt.close(self.fig)

    def _goto(self, new_page):
        # 범위 래핑(원형 넘김)
        if new_page < 0:
            new_page = self.N
        if new_page > self.N:
            new_page = 0
        self.page = new_page
        self._draw_page()

    # ---------- 페이지 렌더 ----------
    def _draw_page(self):
        self.fig.clf()
        if self.mode == "browser":
            if self.page == 0:
                self._draw_overview()
                self.fig.suptitle(f"[0/{self.N}] Overview (Grid) — {self.title}", y=0.98, fontsize=13)
            else:
                self._draw_sensor(self.page - 1)
                self.fig.suptitle(f"[{self.page}/{self.N}] Sensor {self.page} — {self.title}", y=0.98, fontsize=13)
        else:  # scatter 모드
            if self.page == 0:
                self._draw_overview_scatter()
                self.fig.suptitle(f"[0/{self.N}] Scatter Overview (Temp→Pres) — {self.title}", y=0.98, fontsize=13)
            else:
                self._draw_sensor_scatter(self.page - 1)
                self.fig.suptitle(f"[{self.page}/{self.N}] Sensor {self.page} Scatter — {self.title}", y=0.98, fontsize=13)

        self.fig.tight_layout(rect=[0, 0, 1, 0.95])
        self.fig.canvas.draw_idle()

    # ---------- 시계열(원래 코드) ----------
    def _draw_overview(self):
        rows, cols = self.layout
        axes = self.fig.subplots(rows, cols, sharex=True)
        axes = np.atleast_2d(axes).ravel()

        # 전역 범례용 첫 라인 핸들
        h_pres_first = None
        h_temp_first = None

        for i in range(rows * cols):
            ax = axes[i]
            if i < self.N:
                ax_r = ax.twinx()

                hp, = ax.plot(self.time[START_IDX:END_IDX], self.pres[START_IDX:END_IDX, i], linewidth=1.0)
                ht, = ax_r.plot(self.time[START_IDX:END_IDX], self.temp[START_IDX:END_IDX, i], linewidth=1.0, linestyle='--', color='orange')

                if h_pres_first is None: h_pres_first = hp
                if h_temp_first is None: h_temp_first = ht

                ax.set_title(f"S{i+1}", fontsize=9)
                ax.grid(True, linestyle='--', alpha=0.3)

                col_idx = i % cols
                # 좌열/우열에만 y라벨
                if col_idx == 0:
                    ax.set_ylabel("pressure [hPa]", fontsize=8)
                if col_idx == cols - 1:
                    ax_r.set_ylabel("temperature [ºC]", fontsize=8)
                # x라벨은 마지막 행만
                if i // cols == rows - 1:
                    ax.set_xlabel("time [s]", fontsize=8)

                # 필요 시 범위 고정
                # ax.set_ylim(1200, 2500)
                # ax_r.set_ylim(15, 36)
            else:
                ax.set_visible(False)

        if h_pres_first and h_temp_first:
            self.fig.legend([h_pres_first, h_temp_first], ["pres (line)", "temp (line)"],
                            loc="upper center", ncol=2, frameon=False, fontsize=10)

    def _draw_sensor(self, sensor_idx: int):
        ax = self.fig.add_subplot(111)
        ax_r = ax.twinx()

        # 필요 시 범위 고정
        # ax.set_ylim(1200, 2500)
        # ax_r.set_ylim(15, 36)

        hp, = ax.plot(self.time[START_IDX:END_IDX], self.pres[START_IDX:END_IDX, sensor_idx], marker='o', markersize=2, linewidth=0.5, label='pres')
        ht, = ax_r.plot(self.time[START_IDX:END_IDX], self.temp[START_IDX:END_IDX, sensor_idx], marker='s', markersize=2, linewidth=0.5, label='temp',
                        linestyle='--', color='orange')

        ax.set_xlabel("time [s]")
        ax.set_ylabel("pressure [hPa]", rotation=0, labelpad=25, va='center')
        ax_r.set_ylabel("temperature [ºC]", rotation=0, labelpad=25, va='center')

        ax.grid(True, linestyle='--', alpha=0.35)
        ax.set_title(f"Sensor {sensor_idx+1}")

        # 범례
        self.fig.legend([hp, ht], ["pres (line)", "temp (line)"], loc="upper right", frameon=False)

    # ---------- 산점도(Temp(x) vs Pres(y)) : 그리드 + 단일 센서 ----------
    def _draw_overview_scatter(self):
        rows, cols = self.layout
        # 센서 간 비교를 위해 축 범위 통일
        t_min, t_max = np.nanmin(self.temp), np.nanmax(self.temp)
        p_min, p_max = np.nanmin(self.pres), np.nanmax(self.pres)

        axes = self.fig.subplots(rows, cols, sharex=True, sharey=True)
        axes = np.atleast_2d(axes).ravel()

        for i in range(rows * cols):
            ax = axes[i]
            if i < self.N:
                ax.scatter(self.temp[START_IDX:END_IDX, i], self.pres[START_IDX:END_IDX, i],
                           s=self.scatter_ms**2, alpha=self.scatter_alpha, color='#000000', edgecolors='none')
                ax.set_title(f"S{i+1}", fontsize=9)
                ax.grid(True, linestyle='--', alpha=0.3)
                ax.set_xlim(t_min, t_max)
                ax.set_ylim(p_min, p_max)

                col_idx = i % cols
                if col_idx == 0:
                    ax.set_ylabel("pressure [hPa]", fontsize=8)
                if i // cols == rows - 1:
                    ax.set_xlabel("temperature [ºC]", fontsize=8)
            else:
                ax.set_visible(False)

    def _draw_sensor_scatter(self, sensor_idx: int):
        ax = self.fig.add_subplot(111)
        # 전 센서 공통 축 범위(비교 용이)
        t_min, t_max = np.nanmin(self.temp), np.nanmax(self.temp)
        p_min, p_max = np.nanmin(self.pres), np.nanmax(self.pres)

        ax.scatter(self.temp[START_IDX:END_IDX, sensor_idx], self.pres[START_IDX:END_IDX, sensor_idx],
                   s=self.scatter_ms**2, alpha=self.scatter_alpha, color="#00FFFF", edgecolors='#000000')
        ax.set_xlabel("temperature [ºC]")
        ax.set_ylabel("pressure [hPa]")
        ax.grid(True, linestyle='--', alpha=0.35)
        ax.set_title(f"Sensor {sensor_idx+1} — Temp vs Pres")
        ax.set_xlim(t_min, t_max)
        ax.set_ylim(p_min, p_max)

    # ---------- 외부 호출 ----------
    def show(self, mode="browser", **kwargs):
        """
        mode:
        - "browser": 0번(그리드) + ←/→로 센서 넘기는 시계열 뷰어
        - "scatter": 0번(그리드) + ←/→로 센서 넘기는 Temp(x)-Pres(y) 산점도 뷰어
        kwargs (scatter 전용):
        - ms: 마커 크기(포인트)
        - alpha: 투명도
        키:
        - ←/→ : 이전/다음 화면 (0=그리드, 1..N=각 센서)
        - g    : 그리드(0번)로 이동
        - Home/End : 0번/마지막 센서
        - m    : 모드 토글(browser ↔ scatter)
        - q/ESC: 종료
        """
        if 'ms' in kwargs and kwargs['ms'] is not None:
            self.scatter_ms = float(kwargs['ms'])
        if 'alpha' in kwargs and kwargs['alpha'] is not None:
            self.scatter_alpha = float(kwargs['alpha'])

        self.mode = mode
        self.page = 0
        self._draw_page()
        # print("Keys: ←/→ navigate, 'g' grid, Home/End, 'm' toggle mode, 'q'/ESC quit.")
        print_manual_ansi()
        plt.show()

import re
import sys
# try:
#     from wcwidth import wcswidth  # 유니코드 표시 폭 계산
# except Exception:
    # fallback: wcwidth가 없을 때 동작 (대략적, 정확도는 wcwidth가 더 좋음)
import unicodedata
def wcswidth(s: str) -> int:
    s = re.sub(r"\x1b\[[0-9;]*m", "", s)
    w = 0
    for ch in s:
        ea = unicodedata.east_asian_width(ch)
        w += 2 if ea in ("W", "F") else 1
    return w

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def _strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)

def _disp_len(s: str) -> int:
    # ANSI 코드 제거 후 표시 폭 기준 길이
    return wcswidth(_strip_ansi(s))

def make_manual_lines():
    mode = [
        'modes:',
        '- "browser": 0번(그리드) + 센서 시계열',
        '- "scatter": 0번(그리드) + 센서 Temp(x)-Pres(y) 산점도',
    ]
    kwargs = [
        'kwargs (scatter 전용):',
        '- ms (marker size): 마커 크기(pt)',
        '- alpha (opacity): 투명도',
    ]
    keys = [
        'keys:',
        '- ←/→      : 이전/다음 화면 (0=그리드, 1..N=각 센서)',
        '- m        : 모드 토글 (browser ↔ scatter)',
        '- g        : 그리드(0번)로 이동',
        '- Home/End : 0번/마지막 센서',
        '- q/ESC    : 종료',
    ]
    return mode + [''] + keys

def print_manual_ansi():
    BLUE = "\x1b[94m"; CYAN="\x1b[96m"; MAG="\x1b[95m"; BOLD="\x1b[1m"; RESET="\x1b[0m"

    # --- 내용 & 하이라이트 ---
    raw = make_manual_lines()
    lines = []
    for s in raw:
        if not s:
            lines.append("")
            continue
        if s.endswith(':'):
            lines.append(f"{BOLD}{s}{RESET}")
        else:
            s = (s
                 .replace('←/→', f"{BOLD}{CYAN}←/→{RESET}")
                 .replace('Home/End', f"{BOLD}{CYAN}Home/End{RESET}")
                 .replace('"browser"', f'{BOLD}{CYAN}"browser"{RESET}')
                 .replace('"scatter"', f'{BOLD}{CYAN}"scatter"{RESET}')
                 .replace('q/ESC', f'{BOLD}{MAG}q/ESC{RESET}')
                 .replace('ms (marker size)', f'{BOLD}{MAG}ms{RESET} (marker size)')
                 .replace('alpha (opacity)', f'{BOLD}{MAG}alpha{RESET} (opacity)'))
            # ' g ', ' m ' 같은 단독 키워드는 정규식으로 보완
            s = re.sub(r'\b([gm])\b', lambda m: f"{BOLD}{BLUE}{m.group(1)}{RESET}", s)
            lines.append(s)

    # --- 표시 폭 기준으로 박스 폭 계산 ---
    inner_width = max(_disp_len(l) for l in lines) + 2  # 좌우 여백 1칸씩
    top = "┏━" + "━"*inner_width + "━┓"
    bot = "┗━" + "━"*inner_width + "━┛"

    # Windows에서 화살표/한글 깨짐 방지(가능하면)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print(BLUE + top + RESET)
    for ln in lines:
        pad_spaces = inner_width - _disp_len(ln)
        pad = " " * max(0, pad_spaces)
        print(BLUE + "┃ " + RESET + ln + pad + BLUE + " ┃" + RESET)
    print(BLUE + bot + RESET)

if __name__ == "__main__":
    print_manual_ansi()
