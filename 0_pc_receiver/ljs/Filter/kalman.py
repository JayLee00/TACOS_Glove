import numpy as np
from typing import Optional, Dict, Any

class TactileKalmanBatch:
    """
    오프라인 배치용 1차(1D) 칼만 필터 + RTS 스무딩 (채널 벡터화).
    - 상태모델: x_k = x_{k-1} + w,  w ~ N(0, Q)
    - 관측모델: z_k = x_k + v,      v ~ N(0, R)
    Q, R은 스칼라 혹은 (N,) 채널별 벡터 가능.
    타임스탬프 간격(dt) 변동을 Q_eff = Q * dt 로 반영.
    """

    def __init__(
        self,
        num_sensors: int = 21,
        q_pres: float | np.ndarray = (2e-4)**2,  # 압력 단위(질문 코드 기준 prs)에 맞춘 기본값
        r_pres: float | np.ndarray = (2e-3)**2,
        q_temp: float | np.ndarray = (5e-3)**2,  # 온도 단위(질문 코드 기준 tmp)에 맞춘 기본값
        r_temp: float | np.ndarray = (5e-2)**2,
        P0_pres: float = 1.0,
        P0_temp: float = 1.0,
    ):
        self.N = int(num_sensors)

        # 노이즈 설정 (스칼라→채널별 벡터로 확장)
        self.q_pres = self._as_vec(q_pres)
        self.r_pres = self._as_vec(r_pres)
        self.q_temp = self._as_vec(q_temp)
        self.r_temp = self._as_vec(r_temp)

        self.P0_pres = float(P0_pres)
        self.P0_temp = float(P0_temp)

        # 결과 저장용
        self.results: Dict[str, np.ndarray] = {}

    # ---------- public API ----------

    def fit(
        self,
        ts: np.ndarray,
        pres: np.ndarray,   # shape = (T, N)
        temp: np.ndarray,   # shape = (T, N)
        do_smooth: bool = True,
        auto_noise: bool = False,
        auto_win_seconds: float = 1.0,
        hz_hint: Optional[float] = 90.0,
        q_from_r_ratio: float = 0.01,
    ) -> Dict[str, np.ndarray]:
        """
        ts, pres, temp로부터 KF/RTS 결과 계산.
        - auto_noise=True면 앞 구간 분산으로 채널별 R 추정, Q = R * q_from_r_ratio로 설정.
        - 결과 딕셔너리를 반환하고 self.results에도 저장.
        """
        ts = np.asarray(ts, dtype=np.float64).ravel()
        Zp = np.asarray(pres, dtype=np.float64)
        Zt = np.asarray(temp, dtype=np.float64)
        self._validate_inputs(ts, Zp, Zt)
        T1, N1 = Zp.shape
        T2, N2 = Zt.shape

        # 필요 시 채널별 R/Q 자동 추정
        if auto_noise:
            r_p, q_p = self._estimate_noise(Zp, ts[:T1], auto_win_seconds, hz_hint, q_from_r_ratio)
            r_t, q_t = self._estimate_noise(Zt, ts[:T2], auto_win_seconds, hz_hint, q_from_r_ratio)
            self.r_pres, self.q_pres = r_p, q_p
            self.r_temp, self.q_temp = r_t, q_t

        # Forward KF (압력/온도)
        Xp_f, Pp_f, Xp_pred, Pp_pred = self._kf_forward(Zp, ts, self.q_pres, self.r_pres, self.P0_pres)
        Xt_f, Pt_f, Xt_pred, Pt_pred = self._kf_forward(Zt, ts, self.q_temp, self.r_temp, self.P0_temp)

        # RTS smoother (옵션)
        if do_smooth:
            Xp_s, Pp_s = self._rts_smoother(Xp_f, Pp_f, Xp_pred, Pp_pred)
            Xt_s, Pt_s = self._rts_smoother(Xt_f, Pt_f, Xt_pred, Pt_pred)
        else:
            Xp_s = Xp_f.copy();  Pp_s = Pp_f.copy()
            Xt_s = Xt_f.copy();  Pt_s = Pt_f.copy()

        out = {
            "ts": ts,
            "pres_raw": Zp,
            "temp_raw": Zt,
            "pres_kf": Xp_f,
            "temp_kf": Xt_f,
            "pres_rts": Xp_s,
            "temp_rts": Xt_s,
            # 필요 시 공분산도 노출 가능:
            # "pres_Pf": Pp_f, "pres_Ps": Pp_s, "temp_Pf": Pt_f, "temp_Ps": Pt_s
        }
        self.results = out
        return out

    # def save_npz(self, path: str, compress: bool = False, to_float32: bool = True) -> None:
    #     """
    #     fit() 결과를 np.savez(_compressed)로 저장.
    #     - to_float32=True이면 데이터(시계열 제외)를 float32로 줄여서 저장.
    #     """
    #     if not self.results:
    #         raise RuntimeError("No results. Call fit(...) first.")

    #     d = dict(self.results)  # copy
    #     # if to_float32:
    #     #     for k in list(d.keys()):
    #     #         if k == "ts":  # 타임스탬프는 float64 유지 권장
    #     #             continue
    #     #         arr = np.asarray(d[k])
    #     #         # int형(raw가 int로 들어올 수 있음)만 아니면 float32로 축소
    #     #         if np.issubdtype(arr.dtype, np.floating):
    #     #             d[k] = arr.astype(np.float32)

    #     # if compress:
    #     #     np.savez_compressed(path, **d)
    #     # else:
    #     np.savez(path, **d)

    # ---------- helpers ----------

    def _as_vec(self, x: float | np.ndarray) -> np.ndarray:
        return np.full(self.N, float(x), dtype=np.float64) if np.isscalar(x) else np.asarray(x, dtype=np.float64)

    def _validate_inputs(self, ts: np.ndarray, Zp: np.ndarray, Zt: np.ndarray) -> None:
        if Zp.ndim != 2 or Zt.ndim != 2:
            raise ValueError("pres/temp must be 2D arrays (T, N).")
        T1, N1 = Zp.shape
        T2, N2 = Zt.shape
        if N1 != self.N or N2 != self.N:
            raise ValueError(f"channel size mismatch: got {N1}, {N2}, expected {self.N}")
        if T1 != T2 or ts.shape[0] != T1:
            raise ValueError("time/pres/temp length mismatch.")
        if T1 < 2:
            raise ValueError("Need at least 2 samples for smoothing.")

    def _estimate_noise(
        self,
        Z: np.ndarray,
        ts: np.ndarray,
        win_seconds: float,
        hz_hint: Optional[float],
        q_from_r_ratio: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        시작 구간(win_seconds)의 채널별 분산으로 R 추정, Q = R * ratio.
        """
        if hz_hint is not None and hz_hint > 0:
            n = max(8, int(win_seconds * hz_hint))
        else:
            # timestamps로부터 대략 fps 추정
            dt = np.diff(ts)
            med_dt = np.median(dt[dt > 0]) if dt.size else 1.0 / 90.0
            n = max(8, int(win_seconds / max(med_dt, 1e-6)))

        n = min(n, Z.shape[0])
        sigma2 = Z[:n].var(axis=0)  # 채널별 분산
        # 너무 작은 분산에 대한 바닥값
        sigma2 = np.maximum(sigma2, 1e-12)
        R = sigma2
        Q = np.maximum(R * float(q_from_r_ratio), 1e-12)
        return R, Q

    # ---- Core KF/RTS (random-walk, 벡터화) ----

    def _kf_forward(
        self,
        Z: np.ndarray,            # (T, N)
        ts: np.ndarray,           # (T,)
        q_vec: np.ndarray,        # (N,)
        r_vec: np.ndarray,        # (N,)
        P0: float = 1.0,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        T, N = Z.shape
        Xf    = np.zeros((T, N), dtype=np.float64)
        Pf    = np.zeros((T, N), dtype=np.float64)
        Xpred = np.zeros((T, N), dtype=np.float64)
        Ppred = np.zeros((T, N), dtype=np.float64)

        x = np.zeros(N, dtype=np.float64)   # x0 = 0 (필요 시 바꾸려면 인자 추가)
        P = np.full(N, float(P0), dtype=np.float64)

        eps = 1e-12

        for t in range(T):
            if t > 0:
                dt = float(ts[t] - ts[t-1])
                if not np.isfinite(dt) or dt <= 0:
                    dt = 1.0
            else:
                dt = 1.0
            Qeff = q_vec * dt

            # Predict
            x_pred = x
            P_pred = P + Qeff

            # Update
            z = Z[t]
            denom = P_pred + r_vec + eps
            K = P_pred / denom
            x = x_pred + K * (z - x_pred)
            P = (1.0 - K) * P_pred

            Xf[t]    = x
            Pf[t]    = P
            Xpred[t] = x_pred
            Ppred[t] = P_pred

        return Xf, Pf, Xpred, Ppred

    def _rts_smoother(
        self,
        Xf: np.ndarray, Pf: np.ndarray, Xpred: np.ndarray, Ppred: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        Xf    = np.asarray(Xf, dtype=np.float64)
        Pf    = np.asarray(Pf, dtype=np.float64)
        Xpred = np.asarray(Xpred, dtype=np.float64)
        Ppred = np.asarray(Ppred, dtype=np.float64)

        T, N = Xf.shape
        Xs = np.zeros_like(Xf)
        Ps = np.zeros_like(Pf)

        Xs[-1] = Xf[-1]
        Ps[-1] = Pf[-1]
        eps = 1e-12

        for t in range(T - 2, -1, -1):
            C = Pf[t] / (Ppred[t + 1] + eps)  # smoother gain
            Xs[t] = Xf[t] + C * (Xs[t + 1] - Xpred[t + 1])
            Ps[t] = Pf[t] + C * (Ps[t + 1] - Ppred[t + 1]) * C

        return Xs, Ps
