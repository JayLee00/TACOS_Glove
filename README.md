# 2025_Tactile_Sensor

## 라이브러리 경로 세팅
- .ino 폴더가 있는 곳에 src 폴더를 만들고 그 안에 라이브러리 두면 인식 됨
```c
// ex
#include "src/SparkFun_BMP384_Arduino_Library/src/SparkFunBMP384.h"
```

## PC Receiver Result Example
> Serial port COM8 opened successfully.
> STX=0xa5, t_us=1199434288, count=21, vals=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 32]
> STX=0xa5, t_us=1199534652, count=21, vals=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 32]
> STX=0xa5, t_us=200744, count=21, vals=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 32]   
> STX=0xa5, t_us=501848, count=21, vals=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 32]   
> STX=0xa5, t_us=802952, count=21, vals=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 32]   
> STX=0xa5, t_us=1104060, count=21, vals=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 32]

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
