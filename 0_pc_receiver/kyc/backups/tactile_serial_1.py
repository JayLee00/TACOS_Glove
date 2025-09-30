# import sys
# import serial
# from serial import SerialException, SerialTimeoutException
# import struct
# import time
# import threading

# class Tactile_Serial:
#     # Packet 포맷: < = little endian
#     # B = uint8_t, I = uint32_t, B = uint8_t, 21h = 21 * int16_t
#     # B(1) I(4) B(1) 21h(42) -> 총 48바이트
#     packet_format = "<BIB21h"
#     packet_size   = struct.calcsize(packet_format)  # 48

#     def __init__(self, port='COM5', baudrate=115200, timeout=0.1):
#         self.port     = port
#         self.baudrate = baudrate
#         self.timeout  = timeout

#         self.ser = None

#         self._stop_event = threading.Event()
#         self._buf = bytearray()

#         self.vals = []
#         self.timestamp = []

#         self.prev_time = time.time()

#     def open(self):
#         try:
#             self.ser = serial.Serial(
#                 port=self.port,
#                 baudrate=self.baudrate,
#                 parity=serial.PARITY_NONE,
#                 stopbits=serial.STOPBITS_ONE,
#                 bytesize=serial.EIGHTBITS,
#                 timeout=self.timeout  # non-blocking with timeout
#             )
#         except SerialException as e:
#             sys.stderr.write(f"[ERROR] Failed to open '{self.port}': {e}\n"); sys.stderr.flush()
#             sys.exit(3)
#         except (PermissionError, OSError) as e:
#             sys.stderr.write(f"[ERROR] Cannot access '{self.port}' (permission/in-use): {e}\n"); sys.stderr.flush()
#             sys.exit(4)
#         else:
#             if not self.ser.is_open:
#                 self.ser.open()
#             print(f"Serial port {self.ser.port} opened successfully.")

#     def _try_parse_one(self):
#         """
#         링버퍼(self._buf)에서 패킷 하나를 파싱 시도.
#         성공 시 (stx, t_us, count, vals_list)를 반환하고, 버퍼에서 제거.
#         실패/부족 시 None 반환 (버퍼는 부족한 데이터 유지).
#         """
#         # 1) 헤더 찾기
#         idx = self._buf.find(b'\xA5')
#         if idx == -1:
#             # 헤더가 아예 없으면 버퍼를 너무 크게 두지 않도록 정리
#             if len(self._buf) > 2 * self.packet_size:
#                 del self._buf[:-self.packet_size]  # 뒤쪽은 남겨두고 앞쪽 과거는 버림
#             return None

#         # 2) 헤더 앞의 쓰레기 제거
#         if idx > 0:
#             del self._buf[:idx]  # 헤더부터 시작하도록 정리

#         # 3) 패킷 길이 확인
#         if len(self._buf) < self.packet_size:
#             # 아직 모자람 → 더 읽어야 함
#             return None

#         # 4) 후보 패킷 추출
#         pkt = bytes(self._buf[:self.packet_size])

#         # 5) 언팩 시도
#         try:
#             stx, t_us, count, *vals = struct.unpack(self.packet_format, pkt)
#         except struct.error:
#             # 정렬이 아니었음 → 헤더 바이트만 버리고 재시도
#             del self._buf[0:1]
#             return None

#         # 6) 값 검증
#         if stx != 0xA5 or count != 21:
#             # 헤더가 가짜였거나 깨진 프레임 → 한 바이트만 밀고 다시 탐색
#             del self._buf[0:1]
#             return None

#         # (선택) 7) CRC/체크섬 검증 훅
#         # if not self._check_crc(pkt):
#         #     del self._buf[0:1]
#         #     return None

#         # 8) 성공 → 버퍼에서 완전 제거 후 리턴
#         # del self._buf[:self.packet_size]
#         self._buf.clear()
#         return stx, t_us, count, vals

#     def read_loop(self):
#         try:
#             while not self._stop_event.is_set():
#                 # 가용 데이터 읽기 (없으면 1바이트라도 읽어 timeout에 맡김)
#                 n = self.ser.in_waiting
#                 chunk = self.ser.read(n if n > 0 else 1)
#                 time_tmp = time.time()
#                 if chunk:
#                     self._buf.extend(chunk)

#                 # 버퍼에서 가능한 한 많은 패킷을 파싱
#                 while True:
#                     parsed = self._try_parse_one()
#                     if parsed is None:
#                         break
#                     stx, t_us, count, vals = parsed
#                     self.vals = vals.copy()
#                     self.timestamp.append(time_tmp)
#                     print(f"STX={hex(stx)}, t_us={t_us}, count={count}, vals={vals}")
#                     self._buf.clear()
#                     now_time = time.time()
#                     delay_time = now_time - self.prev_time
#                     self.prev_time = now_time
#                     if delay_time == 0:
#                         delay_time = 1
#                     print(f"{1/delay_time} Hz")

#         except (serial.SerialException, SerialTimeoutException) as e:
#             print(f"Serial port error: {e}")
#         except Exception as e:
#             print(f"An unexpected error occurred: {e}")

#     def start_read_loop(self):
#         if getattr(self, "thread", None) and self.thread.is_alive():
#             return
#         self._stop_event.clear()
#         self.thread = threading.Thread(target=self.read_loop, daemon=True)
#         self.thread.start()

#     def stop_read_loop(self):
#         self._stop_event.set()
#         if getattr(self, "thread", None):
#             self.thread.join(timeout=1.0)

#     def close(self):
#         self.stop_read_loop()
#         if self.ser and self.ser.is_open:
#             self.ser.close()
#             print(f"Serial port {self.ser.port} closed.")

#     def __del__(self):
#         try:
#             self.close()
#         except Exception:
#             pass

# if __name__ == "__main__":
#     t_ser = Tactile_Serial(port='COM12', baudrate=115200, timeout=0.1)
#     t_ser.open()
#     t_ser.start_read_loop()
#     try:
#         while True:
#             time.sleep(0.5)
#     except KeyboardInterrupt:
#         t_ser.close()
