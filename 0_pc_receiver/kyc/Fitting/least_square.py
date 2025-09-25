# import os, sys
# sys.path.append(os.getcwd())
import numpy as np
import matplotlib.pyplot as plt
from SaveLoad.load import Load

def load_npz(path):
    """np.savez로 저장한 RTS 보정 데이터를 로드."""
    data = np.load(path, allow_pickle=False)
    temp = np.asarray(data["tactile_temp_rts"])  # (T, N)
    pres = np.asarray(data["tactile_pres_rts"])  # (T, N)
    return temp, pres

def fit_line_lstsq(x, y):
    """
    y ≈ a*x + b 최소제곱 적합.
    반환: a, b, R2, n(유효 샘플 수)
    """
    x = np.asarray(x).ravel()
    y = np.asarray(y).ravel()
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]; y = y[mask]
    n = x.size
    if n < 2 or np.allclose(x.var(), 0.0):
        return np.nan, np.nan, np.nan, n

    # 디자인 행렬 [x, 1]
    A = np.column_stack([x, np.ones_like(x)])
    a, b = np.linalg.lstsq(A, y, rcond=None)[0]

    # R^2
    y_hat = a * x + b
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    R2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else np.nan
    return a, b, R2, n

def fit_all_sensors(temp, pres):
    """
    모든 센서(열)마다 선형 적합 수행.
    반환: results(dict)와 (a,b,R2,n) 배열들
    """
    T, N = pres.shape
    slopes  = np.full(N, np.nan, dtype=float)
    biases  = np.full(N, np.nan, dtype=float)
    r2s     = np.full(N, np.nan, dtype=float)
    counts  = np.zeros(N, dtype=int)

    for j in range(N):
        a, b, R2, n = fit_line_lstsq(temp[:, j], pres[:, j])
        slopes[j] = a
        biases[j] = b
        r2s[j]    = R2
        counts[j] = n

    results = {
        "sensor_idx": np.arange(N),
        "slope_a": slopes,
        "intercept_b": biases,
        "R2": r2s,
        "n": counts,
    }
    return results, slopes, biases, r2s, counts

def plot_overlay_all(temp, pres, slopes, biases, sample_every=1, dot_size=6):
    """
    모든 센서를 한 그래프에 겹쳐서 표시 (빠르게 트렌드 확인).
    sample_every: 점이 너무 많을 때 다운샘플링 간격
    """
    T, N = pres.shape
    plt.figure(figsize=(7, 6))
    for j in range(N):
        x = temp[::sample_every, j]
        y = pres[::sample_every, j]
        m = np.isfinite(x) & np.isfinite(y)
        x = x[m]; y = y[m]
        if x.size == 0:
            continue
        # 산점도
        plt.scatter(x, y, s=dot_size, alpha=0.3)

        # 회귀선 (x 범위를 센서 데이터에 맞게)
        a = slopes[j]; b = biases[j]
        if np.isfinite(a) and np.isfinite(b):
            xx = np.linspace(np.min(x), np.max(x), 100)
            yy = a * xx + b
            plt.plot(xx, yy, linewidth=1)

    plt.xlabel("Temp (x)")
    plt.ylabel("Pres (y)")
    plt.title("Temp vs Pres (All sensors overlay)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_grid(temp, pres, slopes, biases, layout=(3,7), dot_size=8):
    """
    각 센서를 격자(기본 3x7)로 개별 산점도+회귀선 표시.
    """
    T, N = pres.shape
    rows, cols = layout
    assert rows * cols >= N, "layout 칸수보다 센서 수가 많습니다."

    fig, axes = plt.subplots(rows, cols, figsize=(cols*3.1, rows*2.7), squeeze=False)
    k = 0
    for r in range(rows):
        for c in range(cols):
            ax = axes[r, c]
            if k < N:
                x = temp[:, k]
                y = pres[:, k]
                m = np.isfinite(x) & np.isfinite(y)
                x = x[m]; y = y[m]
                ax.scatter(x, y, s=dot_size, alpha=0.5)

                a = slopes[k]; b = biases[k]
                if np.isfinite(a) and np.isfinite(b) and x.size > 0:
                    xx = np.linspace(np.min(x), np.max(x), 100)
                    yy = a * xx + b
                    ax.plot(xx, yy, linewidth=1.5)
                ax.set_title(f"Ch {k}")
                ax.set_xlabel("Temp")
                ax.set_ylabel("Pres")
                ax.grid(True, linestyle="--", alpha=0.4)
            else:
                ax.axis("off")
            k += 1

    fig.suptitle("Temp vs Pres with LS lines (per sensor)")
    plt.tight_layout()
    plt.show()

def results_to_csv(results, out_csv="ls_results.csv"):
    """
    결과 테이블을 CSV로 저장 (sensor_idx, slope_a, intercept_b, R2, n).
    """
    header = "sensor_idx,slope_a,intercept_b,R2,n"
    arr = np.column_stack([
        results["sensor_idx"],
        results["slope_a"],
        results["intercept_b"],
        results["R2"],
        results["n"],
    ])
    np.savetxt(out_csv, arr, delimiter=",", header=header, comments="", fmt=["%d","%.8g","%.8g","%.6f","%d"])
    return out_csv

# ===================== 사용 예시 =====================
if __name__ == "__main__":
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

    # # CSV로 저장
    # out_csv = results_to_csv(results, out_csv="ls_results_rts.csv")
    # print("Saved:", out_csv)
