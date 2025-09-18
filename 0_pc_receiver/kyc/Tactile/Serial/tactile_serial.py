import sys
import serial
from serial import SerialException, SerialTimeoutException
import struct
import time

class Tactile_Serial:
    # Packet 포맷: < = little endian
    # B = uint8_t, I = uint32_t, B = uint8_t, 21H = 21 * uint16_t
    packet_format = "<BIB21H"
    packet_size = struct.calcsize(packet_format)

    def __init__(self, port='COM5', baudrate=115200, timeout=8):
        self.port    = port
        self.baudrate= baudrate
        self.timeout = timeout

        self._datafps = 0
        self._timeSinceConnected = 0.0

    def open(self):
        """public void Open()"""
        try:
            self.ser = serial.Serial(
                        port=self.port,
                        baudrate=self.baudrate,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS,
                        timeout=self.timeout
                        )

        except SerialException as e:
            sys.stderr.write(f"[ERROR] Failed to open '{self.port}': {e}\n")
            sys.stderr.flush()
            sys.exit(3)  # 3: 디바이스 열기 실패 (점유/드라이버 문제 등)
        except (PermissionError, OSError) as e:
            sys.stderr.write(f"[ERROR] Cannot access '{self.port}' (permission/in-use): {e}\n")
            sys.stderr.flush()
            sys.exit(4)  # 4: 권한/OS 레벨 접근 오류
        else:
            #self.ser.open()
            self._datafps = 0#f
            self._timeSinceConnected = time.perf_counter()#Time.realtimeSinceStartup
            # Ensure the port is open
            if not self.ser.is_open:
                self.ser.open()
            print(f"Serial port {self.ser.port} opened successfully.")

    def read(self):
        try:
            while True:
                while self.ser.in_waiting == 0:
                    pass

                header_idx = 0
                data_read = self.ser.read(self.packet_size * 3)
                if data_read:
                    for header_idx in range(self.packet_size * 2):
                        if hex(data_read[header_idx]) == hex(0xa5):
                            break
                    data = data_read[header_idx: self.packet_size + header_idx]
                    if data is None:
                        continue
                    if len(data) == self.packet_size:
                        stx, t_us, count, *vals = struct.unpack(self.packet_format, data)
                        print(f"STX={hex(stx)}, t_us={t_us}, count={count}, vals={vals}")
                
                data = None

        except serial.SerialException as e:
            print(f"Serial port error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def close(self):
        # Close the serial port
        if self.ser.is_open:
            self.ser.close()
            print(f"Serial port {self.ser.port} closed.")

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    t_ser = Tactile_Serial(port='COM8')
    t_ser.open()
    t_ser.read()