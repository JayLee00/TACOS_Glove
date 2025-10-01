# import os, sys
# sys.path.append(os.getcwd())
import numpy as np
import matplotlib.pyplot as plt
from SaveLoad.load import LoadTactile

# def load_npz(path):
#     """np.savez로 저장한 RTS 보정 데이터를 로드."""
#     data = np.load(path, allow_pickle=False)
#     temp = np.asarray(data["tactile_temp_rts"])  # (T, N)
#     pres = np.asarray(data["tactile_pres_rts"])  # (T, N)
#     return temp, pres

def lstsq_fit_line(x, y):
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

def lstsq_fit_all_sensors(temp, pres):
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
        a, b, R2, n = lstsq_fit_line(temp[:, j], pres[:, j])
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



# def results_to_csv(results, out_csv="ls_results.csv"):
#     """
#     결과 테이블을 CSV로 저장 (sensor_idx, slope_a, intercept_b, R2, n).
#     """
#     header = "sensor_idx,slope_a,intercept_b,R2,n"
#     arr = np.column_stack([
#         results["sensor_idx"],
#         results["slope_a"],
#         results["intercept_b"],
#         results["R2"],
#         results["n"],
#     ])
#     np.savetxt(out_csv, arr, delimiter=",", header=header, comments="", fmt=["%d","%.8g","%.8g","%.6f","%d"])
#     return out_csv

# ===================== 사용 예시 =====================
# if __name__ == "__main__":
#     # path = r"./tactile_session_rts.npz"   # <- 네 파일 경로로 교체
#     fn="timestamp_data_250925_160345_t(41962,)P(41962, 21)T(41962, 21)KTrue"
#     l = Load(fn)
#     time = l.data["tactile_time"]
#     # pres = l.data["tactile_pres"]
#     # temp = l.data["tactile_temp"]
#     pres = l.data["tactile_pres_kf"]
#     temp = l.data["tactile_temp_kf"]

#     results, slopes, biases, r2s, counts = fit_all_sensors(temp, pres)

#     # 간단히 화면에 확인
#     for j in range(pres.shape[1]):
#         print(f"Ch{j:02d}  a={slopes[j]:.6g}  b={biases[j]:.6g}  R2={r2s[j]:.4f}  n={counts[j]}")

#     # 오버레이 보기(빠른 트렌드)
#     plot_overlay_all(temp, pres, slopes, biases, sample_every=3, dot_size=5)

#     # 3x7 그리드(21채널) 상세 보기
#     plot_grid(temp, pres, slopes, biases, layout=(3,7), dot_size=6)

#     # # CSV로 저장
#     # out_csv = results_to_csv(results, out_csv="ls_results_rts.csv")
#     # print("Saved:", out_csv)
