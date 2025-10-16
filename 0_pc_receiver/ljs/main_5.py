import os
import sys
import serial
from serial import SerialException
import time
import numpy as np

# 현재 작업 디렉토리를 시스템 경로에 추가
sys.path.append(os.getcwd())
# 기존의 Tactile 데이터 처리 클래스들을 임포트
from Tactile import Tactile, LoadTactile

# --- 사용자 설정 ---
# 1. 센서 데이터 수신 설정
SENSOR_PORT = 'COM6'                # Arduino 센서 보드가 연결된 COM 포트
SENSOR_BAUDRATE = 1_000_000         # 통신 속도
CALIB_FILENAME = "least_square_data_250926_152654" # 사용할 보정 데이터 파일 이름

# 2. 데이터 전달 설정
FORWARD_PORT = 'COM7'               # 데이터를 전달할 가상 시리얼 포트
FORWARD_BAUDRATE = 9600             # 전달용 포트의 통신 속도
SENSOR_INDEX_TO_FORWARD = 12        # 전달할 센서 인덱스 (13번째 값 = 인덱스 12)
# --- ---

def main():
    """
    센서 데이터를 수신하여 보정한 후, 특정 센서 값만 다른 시리얼 포트로 전달합니다.
    """
    print("--- 센서 데이터 포워딩 프로그램 시작 ---")

    # --- 1. 보정 데이터 불러오기 ---
    print(f"보정 파일 '{CALIB_FILENAME}.npz'를 불러옵니다...")
    try:
        l_calib = LoadTactile(CALIB_FILENAME, is_coefficients=True)
        calib_data = l_calib.data
        print("보정 데이터 불러오기 성공.")
        # l_calib.print_data("ls_a") # 필요 시 보정 계수 확인
        # l_calib.print_data("ls_b")
    except FileNotFoundError:
        print(f"[오류] 보정 파일({CALIB_FILENAME}.npz)을 찾을 수 없습니다. 프로그램을 종료합니다.")
        return

    # --- 2. 데이터 전달용 시리얼 포트 열기 ---
    ser_forward = None
    try:
        ser_forward = serial.Serial(FORWARD_PORT, FORWARD_BAUDRATE, timeout=1)
        print(f"전달용 포트 {FORWARD_PORT} 열기 성공.")
        time.sleep(2) # 포트 안정화 대기
    except SerialException as e:
        print(f"[오류] 전달용 포트 {FORWARD_PORT}를 열 수 없습니다: {e}")
        print("가상 시리얼 포트 프로그램(예: com0com)이 실행 중인지 확인하세요.")
        return

    # --- 3. 센서 데이터 수신 시작 ---
    # Tactile 객체는 내부적으로 별도 스레드를 사용하여 데이터를 계속 수신합니다.
    print(f"센서 포트 {SENSOR_PORT}에서 데이터 수신을 시작합니다...")
    tactile_sensor = Tactile(
        port=SENSOR_PORT,
        baudrate=SENSOR_BAUDRATE,
        print_en=False,  # 콘솔이 복잡해지지 않도록 실시간 출력은 끔
        calib_data=calib_data
    )

    # --- 4. 메인 루프: 데이터 추출 및 전달 ---
    print(f"\n{SENSOR_INDEX_TO_FORWARD + 1}번째 센서 값을 {FORWARD_PORT}로 전달합니다. (중지: Ctrl+C)")
    last_sent_value = None
    try:
        while True:
            # Tactile 객체에서 최신 압력/온도 데이터 가져오기
            # 이 값들은 백그라운드 스레드에서 계속 업데이트됩니다.
            current_pres = tactile_sensor.pres
            current_temp = tactile_sensor.temp

            # 데이터가 수신되었는지 확인 (길이가 0이 아닌지)
            if len(current_pres) == 21:
                # 13번째 압력 값 추출
                value_to_send = current_pres[SENSOR_INDEX_TO_FORWARD]

                # 이전 값과 동일하면 보내지 않음 (선택 사항)
                if value_to_send != last_sent_value:
                    # 데이터를 문자열로 변환하고 줄바꿈 문자를 추가
                    # MATLAB 등에서 `readline`으로 쉽게 읽을 수 있음
                    output_str = f"{value_to_send:.4f}\n"

                    # 문자열을 바이트로 인코딩하여 시리얼 포트로 전송
                    ser_forward.write(output_str.encode('utf-8'))

                    # 콘솔에 현재 전송 값과 수신 Hz 출력
                    print(f"\r전송 값: {value_to_send:10.4f} | 수신 속도: {tactile_sensor.data_hz:5.1f} Hz", end="")
                    
                    last_sent_value = value_to_send

            # CPU 사용량을 줄이기 위해 짧은 대기 시간 추가
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n프로그램 종료 중...")
    finally:
        # --- 5. 종료 처리 ---
        tactile_sensor.close() # 센서 수신 스레드 및 포트 종료
        if ser_forward and ser_forward.is_open:
            ser_forward.close()
            print(f"전달용 포트 {FORWARD_PORT}가 닫혔습니다.")
        print("프로그램이 종료되었습니다.")


if __name__ == "__main__":
    main()
