import os
import sys
import time
import serial
from serial import SerialException
import struct

# --- Matplotlib 백엔드 설정 ---
# 이 스크립트는 GUI를 사용하지 않으므로, 'agg' (Non-GUI) 백엔드를 명시적으로 설정합니다.
# 이 코드는 Tactile 모듈이 내부적으로 matplotlib를 불러오기 전에 실행되어야 합니다.
import matplotlib
matplotlib.use('agg')

# 현재 작업 디렉토리를 시스템 경로에 추가
sys.path.append(os.getcwd())
from Tactile import Tactile

# --- 사용자 설정 ---
SENSOR_PORT = 'COM9'                # 센서 보드가 연결된 COM 포트 (데이터 수신용)
SENSOR_BAUDRATE = 1_000_000         # 수신용 통신 속도
SENSOR_INDEX_TO_FORWARD = 4        # 전달할 센서 인덱스 (13번째 센서 = 인덱스 12)

# --- MATLAB으로 데이터 전달을 위한 설정 ---
FORWARD_PORT = 'COM12'              # MATLAB이 읽을 가상 시리얼 포트
FORWARD_BAUDRATE = 9600             # MATLAB과 맞출 통신 속도

def main():
    """
    Tactile 센서 데이터를 수신하여 특정 센서의 압력 값만 터미널에 출력하고,
    다른 시리얼 포트(COM12)를 통해 MATLAB으로 전송합니다.
    """
    print("--- 센서 데이터 MATLAB 전송 프로그램 시작 ---")

    # --- 데이터 전달용 시리얼 포트(COM12) 열기 ---
    ser_forward = None
    try:
        # write_timeout을 설정하여 MATLAB이 데이터를 읽지 않을 때 프로그램이 멈추는 것을 방지
        ser_forward = serial.Serial(
            FORWARD_PORT, FORWARD_BAUDRATE, timeout=1, write_timeout=1
        )
        print(f"MATLAB 전송용 포트 {FORWARD_PORT} 열기 성공.")
        time.sleep(2) # 포트 안정화를 위해 잠시 대기
    except SerialException as e:
        print(f"[오류] 전송용 포트 {FORWARD_PORT}를 열 수 없습니다: {e}")
        print("가상 시리얼 포트 프로그램(com0com 등)이 실행 중인지 확인하세요.")
        return

    # 1. Tactile 객체 생성 및 수신 시작
    print(f"센서 포트 {SENSOR_PORT}에서 데이터 수신을 시작합니다...")
    tactile_sensor = Tactile(
        port=SENSOR_PORT,
        baudrate=SENSOR_BAUDRATE,
        print_en=False  # 터미널 출력을 간결하게 유지하기 위해 내부 출력 기능은 끔
    )

    print(f"\n{SENSOR_INDEX_TO_FORWARD + 1}번째 센서 압력 값을 {FORWARD_PORT}로 전송합니다. (중지: Ctrl+C)")

    # 2. 메인 루프: 데이터 가져오기 및 출력
    try:
        while True:
            # Tactile 객체에서 최신 데이터를 가져옵니다.
            pres, temp, cnt, hz, miss_cnt = tactile_sensor.get_all_data()

            # 데이터가 정상적으로 수신되었는지 확인 (센서 개수 21개)
            if len(pres) == 21:
                # 13번째 압력 값 (인덱스 12) 추출
                specific_sensor_value = pres[SENSOR_INDEX_TO_FORWARD]

                # 터미널에 해당 값과 수신 속도(Hz)를 출력
                # \r은 줄바꿈 없이 현재 줄을 덮어쓰게 하여 깔끔하게 보입니다.
                print(f"\rSensor #{SENSOR_INDEX_TO_FORWARD + 1} Pressure: {specific_sensor_value:10.4f} | Hz: {hz:5.1f} -> {FORWARD_PORT}", end="")

                # # --- 시리얼 포트로 압력 값(int16_t) 전송 ---
                # # 1. 압력 값(float)을 반올림하여 정수로 변환합니다. (예: 1170.1432 -> 1170)
                # int_value = int(round(specific_sensor_value))
                # # 2. 정수 값을 2바이트 signed integer (int16_t, little-endian)로 패킹합니다.
                # output_bytes = struct.pack('<h', int_value)

                # --- 시리얼 포트로 압력 값(double) 전송 ---
                # 1. 압력 값(float)을 8바이트 double (little-endian)으로 패킹합니다.
                output_bytes = struct.pack('<d', specific_sensor_value)


                try:
                    ser_forward.write(output_bytes)
                    ser_forward.flush() # 버퍼를 비워 데이터를 즉시 전송합니다.
                except serial.SerialTimeoutException:
                    # 수신측(MATLAB)이 데이터를 읽지 않아 쓰기 타임아웃 발생
                    # 프로그램을 중단하지 않고 경고만 출력 후 계속 진행합니다.
                    print(f"\n[경고] {FORWARD_PORT} 쓰기 시간 초과. MATLAB이 데이터를 읽고 있는지 확인하세요.", end="")

            # CPU 사용량을 줄이기 위해 짧은 대기 시간 추가
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다...")
    finally:
        # 3. 종료 처리
        if ser_forward and ser_forward.is_open:
            ser_forward.close()
            print(f"\n전송용 포트 {FORWARD_PORT}가 닫혔습니다.")
        
        # Tactile 객체 내부의 TactileSerial 객체를 닫습니다.
        # 'Tactile' 클래스 자체에는 close() 메서드가 없습니다.
        if hasattr(tactile_sensor, 't_ser'):
            tactile_sensor.t_ser.close()
        else:
            print("\n[경고] tactile_sensor.t_ser 객체를 찾을 수 없어 닫지 못했습니다.")


if __name__ == "__main__":
    main()
