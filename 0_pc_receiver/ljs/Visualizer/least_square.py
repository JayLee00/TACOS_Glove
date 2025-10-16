import numpy as np
import matplotlib.pyplot as plt

def lstsq_plot_overlay_all(temp, pres, slopes, biases, sample_every=1, dot_size=6):
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

    plt.xlabel("temperature [ºC]")
    plt.ylabel("pressure [hPa]")
    plt.title("Temp vs Pres (All sensors overlay)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def lstsq_plot_grid(temp, pres, slopes, biases, layout=(3,7), dot_size=8):
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
                ax.scatter(x, y, s=dot_size, alpha=0.5, color='orange')

                a = slopes[k]; b = biases[k]
                if np.isfinite(a) and np.isfinite(b) and x.size > 0:
                    xx = np.linspace(np.min(x), np.max(x), 100)
                    yy = a * xx + b
                    ax.plot(xx, yy, linewidth=2.5, color='black')
                ax.set_title(f"Sensor {k+1}")
                ax.set_xlabel("temperature [ºC]")
                ax.set_ylabel("pressure [hPa]")
                ax.grid(True, linestyle="--", alpha=0.4)
            else:
                ax.axis("off")
            k += 1

    fig.suptitle("Temp vs Pres with LS lines (per sensor)")
    plt.tight_layout()
    plt.show()