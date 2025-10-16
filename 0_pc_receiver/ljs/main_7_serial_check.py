import sys
import time
import threading
import serial
from serial import SerialException

# --- 사용자 설정 ---
PORT = 'COM12'      # 테스트할 가상 COM 포트
BAUDRATE = 9600    # 통신 속도 (데이터를 보내는 프로그램과 일치해야 함)

# 읽기 스레드를 제어하기 위한 이벤트
stop_event = threading.Event()

def read_from_port(ser):
    """시리얼 포트로부터 데이터를 지속적으로 읽어 화면에 출력하는 함수"""
    print(f"\n[{PORT}] 포트에서 수신 대기 중...")
    while not stop_event.is_set():
        try:
            # 데이터가 들어올 때까지 대기 (readline은 blocking 함수)
            if ser.in_waiting > 0:
                line = ser.readline()
                if line:
                    # 수신된 바이트를 문자열로 디코딩하여 출력
                    # utf-8로 디코딩 시도, 실패하면 무시
                    received_data = line.decode('utf-8', errors='ignore').strip()
                    print(f"<- 수신: {received_data}")

        except SerialException:
            print(f"[{PORT}] 포트 연결이 끊어졌습니다.")
            break
        except Exception as e:
            # KeyboardInterrupt 등 다른 예외 처리
            break

def main():
    """메인 함수: 포트를 열고, 읽기/쓰기 로직을 관리합니다."""
    ser = None
    try:
        # --- 1. 시리얼 포트 열기 ---
        print(f"가상 포트 [{PORT}] (Baud: {BAUDRATE}) 연결을 시도합니다...")
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        print(f"[{PORT}] 연결 성공!")

        # --- 2. 데이터 읽기 스레드 시작 ---
        # 메인 스레드가 사용자 입력을 처리하는 동안,
        # 별도 스레드는 백그라운드에서 계속 데이터를 수신합니다.
        read_thread = threading.Thread(target=read_from_port, args=(ser,))
        read_thread.daemon = True  # 메인 프로그램 종료 시 스레드도 함께 종료
        read_thread.start()

        # --- 3. 사용자 입력 받아 데이터 전송 ---
        print("\n전송할 메시지를 입력 후 Enter를 누르세요. (종료: 'exit')")
        while True:
            # 사용자 입력 대기
            output_data = input("-> 전송: ")

            if output_data.lower() == 'exit':
                print("프로그램을 종료합니다.")
                break

            # 입력된 문자열을 바이트로 인코딩하여 시리얼 포트로 전송
            # \n (줄바꿈)을 추가하여 수신측에서 readline()으로 쉽게 읽도록 함
            ser.write(f"{output_data}\n".encode('utf-8'))

    except SerialException as e:
        print(f"[오류] 포트 [{PORT}]를 열 수 없습니다: {e}")
        print("가상 포트 프로그램(com0com 등)이 실행 중인지, 다른 프로그램이 사용 중이지 않은지 확인하세요.")
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C 또는 Ctrl+Z 입력 시 종료
        print("\n프로그램을 종료합니다.")
    finally:
        # --- 4. 종료 처리 ---
        stop_event.set()  # 읽기 스레드에 종료 신호 전송
        if ser and ser.is_open:
            ser.close()
            print(f"[{PORT}] 포트가 닫혔습니다.")

if __name__ == "__main__":
    main()
