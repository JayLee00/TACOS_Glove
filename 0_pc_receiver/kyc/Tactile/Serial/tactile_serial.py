import sys
import serial
from serial import SerialException, SerialTimeoutException
import struct
import time
import threading

import numpy as np

class Tactile_Serial:
    # Packet 포맷: < = little endian
    packet_format = "<HHB21h21hH"   # stx(2) cnt(2) size(1) pres(42) temp(42) etx(2)
    packet_size   = struct.calcsize(packet_format)  # 91
    
    STX = 0xFFAA
    ETX = 0xAAFF
    EXPECTED_SIZE = packet_size  # 91

    NUM_SENSORS = 21

    def __init__(self, port='COM12', baudrate=1_000_000, timeout=0.1):
        self.port     = port
        self.baudrate = baudrate
        self.timeout  = timeout

        self.ser = None

        self._stop_event = threading.Event()
        self._buf = bytearray()

        self.pres = []
        self.temp = []
        self.timestamp = []

        self.prev_time = time.time()

    def open(self):
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=self.timeout  # non-blocking with timeout
            )
        except SerialException as e:
            sys.stderr.write(f"[ERROR] Failed to open '{self.port}': {e}\n"); sys.stderr.flush()
            sys.exit(3)
        except (PermissionError, OSError) as e:
            sys.stderr.write(f"[ERROR] Cannot access '{self.port}' (permission/in-use): {e}\n"); sys.stderr.flush()
            sys.exit(4)
        else:
            if not self.ser.is_open:
                self.ser.open()
            print(f"Serial port {self.ser.port} opened successfully.")

    def _consume(self, n: int):
        """버퍼에서 정확히 n바이트만 소비."""
        del self._buf[:n]

    def _try_parse_one(self):
        """
        링버퍼(self._buf)에서 패킷 하나를 파싱 시도.
        성공 시 (stx, t_us, size, vals_list, etx)를 반환하고, 버퍼에서 제거.
        실패/부족 시 None 반환 (버퍼는 부족한 데이터 유지/또는 헤더 1바이트만 소비).
        """
        # 1) 2바이트 헤더 시그니처 찾기 (리틀엔디안: 0xFFAA -> b"\xAA\xFF")
        hdr = self.STX.to_bytes(2, "little")
        idx = self._buf.find(hdr)
        if idx == -1:
            # 헤더가 없으면 오래된 쓰레기만 정리
            if len(self._buf) > 2 * self.packet_size:
                del self._buf[:-self.packet_size]
            return None

        # 2) 헤더 앞의 쓰레기 제거
        if idx > 0:
            del self._buf[:idx]

        # 3) 길이 확인
        if len(self._buf) < self.packet_size:
            return None

        # 4) 후보 패킷 추출
        pkt = bytes(self._buf[:self.packet_size])

        # 5) 언팩 시도
        try:
            stx, cnt, size, *rest = struct.unpack(self.packet_format, pkt)
        except struct.error:
            # 정렬 실패/깨짐 → 헤더 한 바이트만 버리고 재시도
            self._consume(1)
            return None

        # rest = 21h(pres) + 21h(temp) + H(etx)
        pres = rest[:21]
        temp = rest[21:42]
        etx  = rest[42]

        # 6) 필드 검증
        if stx != self.STX:
            self._consume(1)
            return None

        # size=전체길이(49) 전제
        if size != self.EXPECTED_SIZE:
            # 길이 깨짐 → 한 바이트만 밀고 재시도
            self._consume(1)
            return None

        if len(pres) != self.NUM_SENSORS or len(temp) != self.NUM_SENSORS:
            # 값 개수 불일치 → 한 바이트만 밀기
            self._consume(1)
            return None

        if etx != self.ETX:
            # 꼬리표 불일치 → 한 바이트만 밀기
            self._consume(1)
            return None

        # 7) 성공 → 버퍼에서 해당 패킷 길이만 소비하고 리턴
        self._consume(self.packet_size)
        # self._buf.clear()
        return stx, cnt, size, pres, temp, etx

    def read_loop(self):
        try:
            while not self._stop_event.is_set():
                # 가용 데이터 읽기 (없으면 1바이트라도 읽어 timeout에 맡김)
                n = self.ser.in_waiting
                chunk = self.ser.read(n if n > 0 else 1)
                time_tmp = time.time()
                if chunk:
                    self._buf.extend(chunk)

                # 버퍼에서 가능한 한 많은 패킷을 파싱
                while True:
                    parsed = self._try_parse_one()
                    if parsed is None:
                        break
                    stx, cnt, size, pres, temp, etx = parsed

                    # 데이터 처리
                    self.pres = list(pres) # 압력(int16, hPa)
                    temp = np.array(temp, dtype=np.float64)
                    tmp = temp / 100.0
                    self.temp = list(tmp) # 온도(int16)
                    self.timestamp.append(time_tmp)

                    print(f"STX={hex(stx)}, cnt={cnt}, size={size}, ETX={hex(etx)}, pres={self.pres}, temp={self.temp}", end=" ")

                    now_time = time.time()
                    delay_time = now_time - self.prev_time
                    self.prev_time = now_time
                    if delay_time <= 0:
                        delay_time = 1e-9
                    print(f"{1.0/delay_time:.3f} Hz", end="\n")

        except (serial.SerialException, SerialTimeoutException) as e:
            print(f"Serial port error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def start_read_loop(self):
        if getattr(self, "thread", None) and self.thread.is_alive():
            return
        self._stop_event.clear()
        self.thread = threading.Thread(target=self.read_loop, daemon=True)
        self.thread.start()

    def stop_read_loop(self):
        self._stop_event.set()
        if getattr(self, "thread", None):
            self.thread.join(timeout=1.0)

    def close(self):
        self.stop_read_loop()
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Serial port {self.ser.port} closed.")

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

if __name__ == "__main__":
    t_ser = Tactile_Serial(port='COM12', baudrate=1_000_000, timeout=0.1)
    t_ser.open()
    t_ser.start_read_loop()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        t_ser.close()
