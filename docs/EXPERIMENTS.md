# TACOS Glove — 실험·코드 정리

최근 실험 파이프라인, 펌웨어 진화, 글러브 코드, PC 처리 흐름을 정리한 문서입니다.

---

## 1. 최신 활성 파이프라인 (2026-02 기준)

### A. 통합 글러브 — 관절 + 촉각 (메인)

| 단계 | 파일 | 설명 |
|------|------|------|
| **펌웨어** | [`3_Mega2560Pro_mini/ljs/7_encoder_tactile/20260215_encoder_tactile/20260215_encoder_tactile.ino`](../3_Mega2560Pro_mini/ljs/7_encoder_tactile/20260215_encoder_tactile/20260215_encoder_tactile.ino) | MCP3208 16관절 + BMP384 21채널 통합 |
| **PC 수신** | [`0_pc_receiver/ljs/encoder_tactile_receiver.py`](../0_pc_receiver/ljs/encoder_tactile_receiver.py) | 37값 CSV 파싱, tactile delta → target joint |

**출력 형식 (115200 baud):**

```
joint0,joint1,...,joint15,tactile0,tactile1,...,tactile20
```

- **joint**: MCP3208 ADC → `map(IN_START, IN_END → OUT_START, OUT_END)` → constrain
- **tactile**: BMP384 상대 압력 (Pa, 부팅 offset 기준, 소수점 2자리)

**주요 기능:**
- BMP384 초기화 10회 재시도 + 실패 센서 2차 연결
- 런타임 센서 재연결 (연속 10회 실패 시, 5초 간격)
- CS 핀 8~28, SPI 1 MHz

---

### B. 관절만 — ROS 2 / 로봇 손 제어

| 단계 | 파일 | 설명 |
|------|------|------|
| **펌웨어** | [`5_TACOS_Glove/ljs/TACOS_Glove_OUT_DATA/TACOS_Glove_OUT_DATA.ino`](../5_TACOS_Glove/ljs/TACOS_Glove_OUT_DATA/TACOS_Glove_OUT_DATA.ino) | 16관절 mapped 값 출력 |
| **캘리브레이션** | [`5_TACOS_Glove/ljs/20260204_calibration_data.txt`](../5_TACOS_Glove/ljs/20260204_calibration_data.txt) | 링크별 ADC min/max |

**출력 형식 (115200 baud, ~100 Hz):**

```
val0,val1,...,val15
```

- Python `readline()` / ROS 2 시리얼 노드와 호환
- EMA 필터 (α=0.02, 현재 raw pass-through)
- Spread 관절 (L4, L8, L12): ±1000 constrain
- Thumb Rotation (L1): ±4096

**최근 수정 (2026-02):** Index L5 `IN_START[5]` = 1900 (기존 2385)

---

### C. 고속 촉각 수집 + 온도 보정

| 단계 | 파일 | 설명 |
|------|------|------|
| **펌웨어** | [`4_tactile_MegaPM_temp.ino`](../3_Mega2560Pro_mini/ljs/4_tactile_MegaPM_temp/4_tactile_MegaPM_temp.ino) | 0xFFAA 바이너리, pres+temp×21 |
| **수집** | `main_1_data_collect_save_show.py` | 실시간 + Kalman + `.npz` 저장 |
| **fitting** | `main_3_1_data_load_fitting_save_show.py` | `pres ≈ a·temp + b` 채널별 적합 |
| **적용** | `main_4_2_apply_calib_data_save_show.py` | 보정 실시간 시각화 |

**바이너리 패킷 (133 bytes, 1 Mbps, ~90 Hz):**

```
STX 0xFFAA (2B) | cnt (2B) | size=133 (1B)
| pres[21] uint32 ×100 (84B) | temp[21] int16 ×100 (42B)
| ETX 0xAAFF (2B)
```

PC 디코딩 (`tactile_serial.py`):
- `pres_hPa = pres_raw / 10000.0`
- `temp_°C = temp_raw / 100.0`

---

### D. 촉각 단독 디버그

| 펌웨어 | 용도 |
|--------|------|
| [`8_tactile_only.ino`](../3_Mega2560Pro_mini/ljs/8_tactile_only/8_tactile_only.ino) | 텍스트 `[v1,...,v21]`, 1 Mbps |
| [`5_tactile_MegaPM_pres_all_data.ino`](../3_Mega2560Pro_mini/ljs/5_tactile_MegaPM_pres_all_data/5_tactile_MegaPM_pres_all_data.ino) | 실패 센서 skip, DEBUG 모드, 115200 |

---

## 2. Mega2560 Pro Mini 펌웨어 진화 (`3_Mega2560Pro_mini/ljs/`)

| # | 스케치 | 프로토콜 | 특징 |
|---|--------|----------|------|
| 1 | `1_tactile_MegaPM_binary_packet_offset` | STX 0xA5, int16×21 | 부팅 offset, 115200 |
| 2 | `2_tactile_MegaPM_timer_interrupt` | 0xA5 + Timer2 ~90Hz | 1 Mbps |
| 3 | `3_tactile_MegaPM_packet_tail` | 0xA5 + ETX 0x5A (49B) | 패킷 tail 추가 |
| 4 | `4_tactile_MegaPM_temp` | **STX 0xFFAA** (133B) | pres+temp, PC 표준 |
| 5 | `5_tactile_MegaPM_pres_all_data` | 텍스트 `[...]` | 디버그용 |
| 6 | `6_tactile_sensor_experiment` | 0xFFAA (133B) | 센서 #0 skip, CS 22~42, 재료 실험 |
| 7 | **`7_encoder_tactile`** | **37값 CSV** | **관절+촉각 통합 — 최신** |
| 8 | `8_tactile_only` | 텍스트 `[...]` | 촉각 단독 간소화 |

---

## 3. 글러브 코드 (`5_TACOS_Glove/ljs/`)

| 폴더 / 파일 | 역할 |
|-------------|------|
| **TACOS_Glove_OUT_DATA** | ROS 2용 16관절 mapped CSV 출력 |
| **TACOS_Raw_16** | MCP3208 raw + EMA, `0:val 1:val ...` 디버그 형식 |
| **01_Glove_Calibration/calibration_Code** | A0~A11 analog raw → `Raw: A[0]554 ...` |
| **Encoder_EXP** | 포텐셜미터 raw 수집 + `Plot_mat.m` |
| **Tatos_Analog_receive** | A0~A11 → `[v0 v1 ... 0 0 0 0]` (9600 baud) |
| **debuging_Raw_data** | KISTAR Hand MCP3208 vs Arduino analog 필터 비교 |

### 관절 매핑 테이블 (공통)

`IN_START[16]`, `IN_END[16]` — ADC 캘리브레이션 min/max  
`OUT_START[16]`, `OUT_END[16]` — 목표 encoder 범위

```c
// 예: Index L4 (Spread, link 4)
IN_START[4] = 2590,  IN_END[4] = 1620
OUT_START[4] = 2048, OUT_END[4] = -2048   // +45° → 2048, -45° → -2048
```

현재 적용값 (`20260215_encoder_tactile`, `TACOS_Glove_OUT_DATA` 공통):

```
IN_START:  2220, 2967, 2060, 2230, 2590, 1900, 2042, 1963,
           2625, 1744, 2317, 2112, 2170, 1607, 1736, 1985
IN_END:    1130,  813, 3189, 1100, 1620, 1170,  960, 3096,
           1552,  874, 1194, 3205, 1103,  844,  608, 3143
```

---

## 4. PC 수신 파이프라인 (`0_pc_receiver/ljs/`)

### 통합 글러브 수신

[`encoder_tactile_receiver.py`](../0_pc_receiver/ljs/encoder_tactile_receiver.py)

```python
PORT = "COM6"       # Arduino 포트 수정
BAUDRATE = 115200
TACTILE_TO_JOINT_SCALE = 0.0  # 0 = joint만, >0 = tactile 보정 활성
OUTPUT_MODE = "summary"       # "summary" | "target" | "full"
```

처리 흐름:
1. 37값 CSV 파싱 → joints[16], tactiles[21]
2. tactile delta force 계산
3. (옵션) delta → joint correction → target joint
4. 출력

### 촉각 보정 체인

```
main_1  수집 + Kalman + 저장 (.npz)
   ↓
main_3_1  채널별 pres ≈ a·temp + b fitting → least_square_data_*.npz
   ↓
main_4_2  보정 적용 실시간 수집 + 시각화
```

### 기타 유틸

| 스크립트 | 용도 |
|----------|------|
| `main_2_data_load_show.py` | 저장 `.npz` scatter 시각화 |
| `main_4_3_only_calib_data_show.py` | 보정 전 raw만 시각화 |
| `main_5.py` | 보정 1채널 → 다른 COM 포워딩 |
| `main_6_only_one_data.py` | 1채널 → MATLAB 가상 COM (9600) |
| `main_7_serial_check.py` | 가상 시리얼 수신 테스트 |

### 모듈 구조

```
Tactile/
  tactile.py              # TactileSerial 래퍼
  Serial/tactile_serial.py  # 0xFFAA 파서
Filter/kalman.py          # 1D Kalman + RTS
Fitting/least_square.py   # pres-temp fitting
SaveLoad/save.py, load.py # .npz I/O
Visualizer/               # Graph, SensorBrowser, matplot
```

---

## 5. MATLAB 실험 (`4_MATLAB/`)

[`4_MATLAB/README.txt`](../4_MATLAB/README.txt) — 실험 노트

| 날짜 | 내용 |
|------|------|
| 2025-10-10 | force-센서 캘리브레이션, `main_6` → MATLAB DAQ/Simulink 연동 |
| 2025-11-09 | 센서 셀별 재료 실험 — 3mm 변형에서 ~5N까지 측정 |

**연동 흐름:**
```
Arduino (6_tactile) → PC (main_6) → 가상 COM → MATLAB DAQ/Simulink
Optosigma 모터스테이지 + 힘 센서 (로컬, gitignore)
```

**Encoder 분석:** [`5_TACOS_Glove/ljs/Encoder_EXP/Plot_mat.m`](../5_TACOS_Glove/ljs/Encoder_EXP/Plot_mat.m)

---

## 6. 캘리브레이션 기록

### 관절 ADC (`20260204_calibration_data.txt`)

| 손가락 | Link | ADC Pin | +90° | -90° / 기타 |
|--------|------|---------|------|-------------|
| Thumb | L0 | — | 2340 | 1815 |
| Thumb | L1 | — | 1750 | 1181 (-90), 2327 (+90) |
| Index | L4 | A7 | 1958 | 1730 (+45), 2455 (-45) |
| Index | L5 | A6 | 2203 | 1645 (+90) |
| Middle | L8 | A11 | 2190 | 1948 (+45), 2460 (-45) |
| Ring | L12 | A11 | 1678 | 1425 (+45), 1973 (-45) |

전체 16링크: [`5_TACOS_Glove/ljs/20260204_calibration_data.txt`](../5_TACOS_Glove/ljs/20260204_calibration_data.txt)

### 촉각 온도 보정

1. `main_1`으로 pres/temp 시계열 수집 (`.npz`)
2. `main_3_1`에서 채널별 `pres ≈ a·temp + b` fitting
3. 계수 저장: `OFFSET_TABLE/least_square_data_*.npz`
4. `main_4_2` 또는 `Tactile.get_calibrated_data()`로 실시간 적용

---

## 7. 알려진 하드웨어 이슈

| 항목 | 상태 | 조치 |
|------|------|------|
| 센서 #6 (검지 MCP1) | 불량 | 값 미출력, 펌웨어에서 skip |
| 센서 #9 (중지 PIP) | 플라스틱 교체 필요 | 재실험 예정 |
| 새끼손가락 | 유격 과다 | 빨간 포텐셜미터 교체 예정 |
| 엄지 | 설계 미흡 | 재설계 예정 |

출처: [`5_TACOS_Glove/ljs/ReadMe.txt`](../5_TACOS_Glove/ljs/ReadMe.txt), [`6번이 3번째 망가진애.txt`](../5_TACOS_Glove/ljs/6번이%203번째%20망가진애.txt)

---

## 8. 권장 실험 순서 (신규 사용자)

```
1. 8_tactile_only.ino          → 시리얼 모니터로 21채널 확인
2. calibration_Code.ino        → 관절 ADC min/max 기록
3. TACOS_Glove_OUT_DATA.ino    → 16관절 mapped 값 확인
4. 20260215_encoder_tactile    → 37값 통합 확인
5. encoder_tactile_receiver.py → PC 수신 + target joint
6. main_1 → main_3_1 → main_4_2 → 온도 보정 파이프라인
```

**작업 디렉터리:** PC 스크립트는 반드시 `0_pc_receiver/ljs/`에서 실행.
