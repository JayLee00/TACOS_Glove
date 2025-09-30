# import sys
# import serial
# from serial import SerialException, SerialTimeoutException
# import struct
# import time
# import threading

# class Tactile_Serial:
#     # Packet 포맷: < = little endian
#     # B = uint8_t, I = uint32_t, B = uint8_t, 21h = 21 * int16_t
#     packet_format = "<BIB21h"
#     packet_size = struct.calcsize(packet_format)

#     def __init__(self, port='COM5', baudrate=115200, timeout=8):
#         self.port    = port
#         self.baudrate= baudrate
#         self.timeout = timeout

#         self._datafps = 0
#         self._timeSinceConnected = 0.0

#         self.vals = []
#         self.timestamp = []

#         self._stop_event = threading.Event()# thread 작동 중 중단 가능하도록 함

#     def open(self):
#         """public void Open()"""
#         try:
#             self.ser = serial.Serial(
#                         port=self.port,
#                         baudrate=self.baudrate,
#                         parity=serial.PARITY_NONE,
#                         stopbits=serial.STOPBITS_ONE,
#                         bytesize=serial.EIGHTBITS,
#                         timeout=self.timeout
#                         )

#         except SerialException as e:
#             sys.stderr.write(f"[ERROR] Failed to open '{self.port}': {e}\n")
#             sys.stderr.flush()
#             sys.exit(3)  # 3: 디바이스 열기 실패 (점유/드라이버 문제 등)
#         except (PermissionError, OSError) as e:
#             sys.stderr.write(f"[ERROR] Cannot access '{self.port}' (permission/in-use): {e}\n")
#             sys.stderr.flush()
#             sys.exit(4)  # 4: 권한/OS 레벨 접근 오류
#         else:
#             #self.ser.open()
#             self._datafps = 0#f
#             self._timeSinceConnected = time.perf_counter()#Time.realtimeSinceStartup
#             # Ensure the port is open
#             if not self.ser.is_open:
#                 self.ser.open()
#             print(f"Serial port {self.ser.port} opened successfully.")

#     def read_loop(self):
#         try:
#             while not self._stop_event.is_set():
#                 while self.ser.in_waiting == 0:
#                     pass

#                 header_idx = 0
#                 data_read = self.ser.read(self.packet_size * 3)
#                 time_tmp = time.time()
#                 if data_read:
#                     for header_idx in range(self.packet_size * 2):
#                         if hex(data_read[header_idx]) == hex(0xa5):
#                             break
#                     data = data_read[header_idx: self.packet_size + header_idx]
#                     if data is None:
#                         continue
#                     if len(data) == self.packet_size:
#                         stx, t_us, count, *vals = struct.unpack(self.packet_format, data)
#                         if count == 21:
#                             self.vals = vals.copy()
#                             self.timestamp.append(time_tmp)
#                             print(f"STX={hex(stx)}, t_us={t_us}, count={count}, vals={vals}")
#                 # data = None

#         except serial.SerialException as e:
#             print(f"Serial port error: {e}")
#         except Exception as e:
#             print(f"An unexpected error occurred: {e}")
    
#     def start_read_loop(self): #read_loop Thread 함수 시작
#         self.thread = threading.Thread(target=self.read_loop)#, daemon=True)
#         self.thread.start()

#     def close(self):
#         # Close the serial port
#         if self.ser.is_open:
#             self.ser.close()
#             print(f"Serial port {self.ser.port} closed.")

#     def __del__(self):
#         if getattr(self, "thread", None) is not None:
#             self.thread.join(timeout=0.1)

# if __name__ == "__main__":
#     t_ser = Tactile_Serial(port='COM10')
#     t_ser.open()
#     # t_ser.read()