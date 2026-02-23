"""
Encoder + Tactile 시리얼 데이터 수신 및 델타 force → target joint 계산

Arduino 포맷: joint(16) + tactile(21) = 37개 값, 콤마 구분, 115200 baud
예: 3355,490,...,1566,226.48,255.96,...,50.52
"""

import sys
import serial
from serial import SerialException
import time
import numpy as np

# --- 설정 ---
PORT = "COM6"              # Arduino 연결 포트
BAUDRATE = 115200
NUM_JOINTS = 16
NUM_TACTILE = 21
TOTAL_VALS = NUM_JOINTS + NUM_TACTILE  # 37

# 델타 force → joint 보정 스케일 (필요에 따라 조정)
# tactile_delta가 이 스케일로 joint에 반영됨
TACTILE_TO_JOINT_SCALE = 0.0  # 0 = joint만 사용, 원하면 0.01~0.1 등으로 조정

# 출력 모드: "summary"=요약만, "target"=매 프레임 target joint CSV 출력, "full"=전체 데이터
OUTPUT_MODE = "summary"


def parse_line(line: str):
    """
    한 줄 파싱 → (joints, tactiles) 또는 None
    """
    line = line.strip()
    if not line or line.startswith("["):  # 재연결 메시지 등 스킵
        return None
    parts = line.split(",")
    if len(parts) != TOTAL_VALS:
        return None
    try:
        joints = np.array([int(p) for p in parts[:NUM_JOINTS]], dtype=np.int32)
        tactiles = np.array([float(p) for p in parts[NUM_JOINTS:]], dtype=np.float64)
        return joints, tactiles
    except (ValueError, IndexError):
        return None


def compute_delta_force(prev_tactile: np.ndarray, curr_tactile: np.ndarray) -> np.ndarray:
    """택타일 델타 (force 변화량)"""
    if prev_tactile is None or len(prev_tactile) != NUM_TACTILE:
        return np.zeros(NUM_TACTILE)
    return curr_tactile - prev_tactile


def tactile_delta_to_joint_delta(delta_force: np.ndarray) -> np.ndarray:
    """
    델타 force → joint 보정량 변환.
    현재는 합/평균 기반 단순 매핑. 필요 시 센서-관절 매핑 테이블로 확장.
    """
    # 예: 전체 tactile 합의 변화를 모든 관절에 균등 분배 (또는 특정 관절만)
    total_delta = np.sum(np.abs(delta_force))
    # 스케일 적용 후 16개 관절에 분배 (예: 0~3 손가락 등)
    correction = np.zeros(NUM_JOINTS)
    if TACTILE_TO_JOINT_SCALE > 0 and total_delta > 0:
        # 간단 예: 0~4번 joint에만 영향 (엄지~검지 등)
        for j in range(min(5, NUM_JOINTS)):
            correction[j] = TACTILE_TO_JOINT_SCALE * total_delta
    return correction


def compute_target_joint(joints: np.ndarray, delta_force: np.ndarray) -> np.ndarray:
    """target joint = joint + joint_correction(delta_force)"""
    joint_correction = tactile_delta_to_joint_delta(delta_force)
    target = joints.astype(np.float64) + joint_correction
    return np.clip(target, -4096, 4096).astype(np.int32)  # Arduino 출력 범위와 맞춤


def main():
    print("--- Encoder + Tactile 수신 (델타 force → target joint) ---")
    print(f"포트: {PORT}, {BAUDRATE} baud")
    print(f"형식: joint {NUM_JOINTS}개 + tactile {NUM_TACTILE}개 = {TOTAL_VALS}개\n")

    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            timeout=0.01,
        )
        time.sleep(0.5)
        print(f"포트 {PORT} 연결됨.\n")
    except SerialException as e:
        print(f"[오류] 포트 열기 실패: {e}")
        sys.exit(1)

    prev_tactile = None
    line_buf = ""
    count = 0
    last_print = time.perf_counter()

    try:
        while True:
            chunk = ser.read(ser.in_waiting or 1)
            if chunk:
                line_buf += chunk.decode("utf-8", errors="ignore")

            # 줄 단위 파싱
            while "\n" in line_buf or "\r" in line_buf:
                idx = line_buf.find("\n")
                if idx == -1:
                    idx = line_buf.find("\r")
                if idx == -1:
                    break
                line = line_buf[:idx]
                line_buf = line_buf[idx + 1 :].lstrip("\r\n")

                parsed = parse_line(line)
                if parsed is None:
                    # [재연결], 빈 줄, 파싱 실패 등은 무시
                    s = line.strip()
                    if s and not s.startswith("[") and len(s) > 20:
                        print(f"[스킵] {line[:60]}...")
                    continue

                joints, tactiles = parsed
                delta_force = compute_delta_force(prev_tactile, tactiles)
                prev_tactile = tactiles.copy()

                target_joint = compute_target_joint(joints, delta_force)

                count += 1
                now = time.perf_counter()

                if OUTPUT_MODE == "target":
                    # target joint만 CSV로 출력 (다른 프로그램에서 파이프로 받을 때)
                    print(",".join(map(str, target_joint)))
                elif OUTPUT_MODE == "full":
                    # joint, tactile, delta_force, target_joint 모두
                    delta_str = ",".join(f"{d:.2f}" for d in delta_force)
                    target_str = ",".join(map(str, target_joint))
                    print(f"J,{','.join(map(str, joints))}")
                    print(f"T,{','.join(f'{t:.2f}' for t in tactiles)}")
                    print(f"D,{delta_str}")
                    print(f"G,{target_str}")
                else:  # summary
                    if now - last_print >= 0.5:
                        print(f"\r[수신 OK] joint: {list(joints[:4])}... | "
                              f"tactile: {tactiles[0]:.1f}... | "
                              f"Δ합: {np.sum(np.abs(delta_force)):.1f} | "
                              f"target: {list(target_joint[:4])}...", end="")
                        last_print = now

                # --- 여기서 target_joint 사용 ---
                # 예: 로봇 제어, 저장, 네트워크 전송 등
                # your_robot.send(target_joint)
                # ...

    except KeyboardInterrupt:
        print("\n\n종료.")
    finally:
        if ser.is_open:
            ser.close()
            print(f"포트 {PORT} 닫힘.")


if __name__ == "__main__":
    main()
