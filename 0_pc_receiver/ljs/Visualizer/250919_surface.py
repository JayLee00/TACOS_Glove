import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RBFInterpolator  # SciPy >= 1.10 권장

# ==== 원본 3x3 격자 점 ====
x = np.linspace(-1, 1, 3)
y = np.linspace(-1, 1, 3)
X, Y = np.meshgrid(x, y)

# ==== 3개의 Z 데이터 (shape: 3 x 3 x 3) ====
Z_list = np.array([
    [[0.0, 0.5, 0.0],
     [0.5, 2.0, 0.5],
     [3.0, 0.5, 0.2]],

    [[0.0, 0.5, 0.0],
     [0.5, 2.0, 0.5],
     [3.0, 0.5, 0.2]],

    [[0.0, 0.5, 0.0],
     [0.5, 2.0, 0.5],
     [3.0, 0.5, 0.2]],
], dtype=float)

# ==== 촘촘한 격자 공통 준비 ====
margin = 0.3
n = 120
x_min, x_max = x.min() - margin, x.max() + margin
y_min, y_max = y.min() - margin, y.max() + margin
x_dense = np.linspace(x_min, x_max, n)
y_dense = np.linspace(y_min, y_max, n)
X_dense, Y_dense = np.meshgrid(x_dense, y_dense)
XY_dense = np.column_stack([X_dense.ravel(), Y_dense.ravel()])

# ==== Figure & Subplots ====
fig = plt.figure(figsize=(15, 5))  # 가로 3배
for i in range(3):
    Z = Z_list[i]

    # 원래 점
    pts = np.column_stack([X.ravel(), Y.ravel()])
    vals = Z.ravel()

    # 외곽 앵커 포인트 추가
    ring_margin = 0.5
    ring_x = np.array([x.min()-ring_margin, x.max()+ring_margin,
                       x.min()-ring_margin, x.max()+ring_margin])
    ring_y = np.array([y.min()-ring_margin, y.min()-ring_margin,
                       y.max()+ring_margin, y.max()+ring_margin])
    ring_z = np.full_like(ring_x, 0.0, dtype=float)

    pts_aug = np.vstack([pts, np.column_stack([ring_x, ring_y])])
    vals_aug = np.concatenate([vals, ring_z])

    # RBF 보간기
    rbf = RBFInterpolator(
        pts_aug, vals_aug,
        kernel='thin_plate_spline',
        smoothing=0.05
    )

    # 보간
    Z_dense = rbf(XY_dense).reshape(X_dense.shape)

    # ==== 서브플롯 그리기 ====
    ax = fig.add_subplot(1, 3, i+1, projection="3d")
    ax.plot_surface(X_dense, Y_dense, Z_dense,
                    cmap="viridis", alpha=0.95, linewidth=0, antialiased=True)

    # 원본 점 (빨간 점)
    ax.scatter(X, Y, Z, s=80, c="red")

    # 각 점에 정수 값 표시 (검정색)
    for xi, yi, zi in zip(X.ravel(), Y.ravel(), Z.ravel()):
        ax.text(xi, yi, zi + 0.1, f"{int(zi)}",
                color="black", ha="center", va="bottom", fontsize=15, fontweight='bold',
                bbox=dict(facecolor="white", edgecolor="white", boxstyle="round,pad=0.1"))

    # 축/제목 설정
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title(f"Surface {i+1}")
    ax.view_init(elev=85, azim=180)

plt.tight_layout()
plt.show()
