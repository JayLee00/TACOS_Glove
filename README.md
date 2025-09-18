# 2025_Tactile_Sensor

## 라이브러리 경로 세팅
- .ino 폴더가 있는 곳에 src 폴더를 만들고 그 안에 라이브러리 두면 인식 됨
```c
// ex
#include "src/SparkFun_BMP384_Arduino_Library/src/SparkFunBMP384.h"
```

## PC Receiver Result Example
```
Serial port COM10 opened successfully.
STX=0xa5, t_us=144372, count=21, vals=[-2, -6, -6, -5, -5, -7, -4, -2, -2, -7, -2, -6, -6, -4, -1, 0, -2, -3, -2, -2, -2]
STX=0xa5, t_us=242484, count=21, vals=[-5, -15, -17, -14, -13, -16, -11, -7, -6, -15, -5, -16, -14, -6, -2, -2, -4, -4, -4, -4, -4]
STX=0xa5, t_us=340536, count=21, vals=[-7, -22, -24, -20, -21, -22, -19, -9, -10, -23, -8, -23, -22, -9, -4, -4, -6, -7, -7, -7, -5]
STX=0xa5, t_us=438572, count=21, vals=[-9, -27, -30, -25, -28, -28, -25, -11, -13, -31, -11, -29, -27, -9, -6, -5, -6, -9, -8, -8, -7]
```
## Project Structure tree
### [0_pc_receiver](./0_pc_receiver)
  - [kyc](./0_pc_receiver/kyc)
    - [Tactile/tactile.py](./0_pc_receiver/kyc/Tactile)
      - [Serial/tactile_serial.py](./0_pc_receiver/kyc/Tactile/Serial)

### [1_Teensy4_0](./1_Teensy4_0)
  - [kyc](./1_Teensy4_0/kyc)
    - [1_tactile_sensor.ino](./1_Teensy4_0/kyc/1_tactile_sensor/1_tactile_sensor.ino)
    - [2_tactile_sensor.ino](./1_Teensy4_0/kyc/2_tactile_sensor/2_tactile_sensor.ino)
  - [ljs](./1_Teensy4_0/ljs)

### [2_Arduino Mega](./2_Arduino%20Mega)
  - [kyc](./2_Arduino%20Mega/kyc)
    - [1_tactile_Mega.ino](./2_Arduino%20Mega/kyc/1_tactile_Mega/1_tactile_Mega.ino)
  - [ljs](./2_Arduino%20Mega/ljs)

### [3_Mega2560Pro_mini](./3_Mega2560Pro_mini)

### [lib](./lib)
  - [kyc](./lib/kyc)
    - [SparkFun_BMP384_Arduino_Library](./lib/kyc/SparkFun_BMP384_Arduino_Library)
      - [src](./lib/kyc/SparkFun_BMP384_Arduino_Library/src)
  - [ljs](./lib/ljs)
  - [origin](./lib/origin)
    - [SparkFun_BMP384_Arduino_Library](./lib/origin/SparkFun_BMP384_Arduino_Library)
      - [src](./lib/origin/SparkFun_BMP384_Arduino_Library/src)
        - [bmp3_api](./lib/origin/SparkFun_BMP384_Arduino_Library/src/bmp3_api)
