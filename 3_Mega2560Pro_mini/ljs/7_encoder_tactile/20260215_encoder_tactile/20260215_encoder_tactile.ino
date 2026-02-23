#include <SPI.h>
#include "src/SparkFun_BMP384_Arduino_Library/src/SparkFunBMP384.h"

#define SERIAL_BAUD 115200

/******************************************************/
/* 1. MCP3208 (Joint Sensors) 설정                   */
/******************************************************/
const int MCP_CS_1 = 46;
const int MCP_CS_2 = 44;

const int IN_START[16] = {
  2220, 2967, 2060, 2230, 2590, 2385, 2042, 1963,
  2625, 1744, 2317, 2112, 2170, 1607, 1736, 1985
};
const int IN_END[16] = {
  1130, 813, 3189, 1100, 1620, 1170, 960, 3096,
  1552, 874, 1194, 3205, 1103, 844, 608, 3143
};
const int OUT_START[16] = {
  0, -4096, 0, 0, 2048, 0, 0, 0,
  2048, 0, 0, 0, 2048, 0, 0, 0
};
const int OUT_END[16] = {
  4096, 4096, 4096, 4096, -2048, 4096, 4096, 4096,
  -2048, 4096, 4096, 4096, -2048, 4096, 4096, 4096
};

/******************************************************/
/* 2. BMP384 (Tactile Sensors) - 5_tactile 동작 검증 설정 */
/******************************************************/
#define NUM_SENSORS 21
uint32_t bmpClockFrequency = 1000000;  // 1MHz (5_tactile과 동일)

byte bmpCsPins[NUM_SENSORS] = {
    8, 9, 10, 11, 12, 13, 14,
    15, 16, 17, 18, 19, 20, 21,
    22, 23, 24, 25, 26, 27, 28
};

BMP384 pressureSensors[NUM_SENSORS];
double offset[NUM_SENSORS] = {0};
bool sensorOk[NUM_SENSORS] = {false};
uint8_t sensorFailCount[NUM_SENSORS] = {0};  // 연속 실패 횟수
#define FAIL_THRESHOLD 10   // 이 횟수 연속 실패 시 재연결 시도
#define RECONNECT_INTERVAL 5000  // 재연결 시도 간격(ms)
unsigned long lastReconnectAttempt[NUM_SENSORS] = {0}; 

/******************************************************/
/* 함수 정의                                          */
/******************************************************/
int readMCP3208(int csPin, byte channel) {
  // MCP3208은 1MHz~2MHz 권장
  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0)); 
  digitalWrite(csPin, LOW);
  byte controlBlock = 0x06 | ((channel & 0x04) >> 2);
  byte controlByte = (channel & 0x03) << 6;
  SPI.transfer(controlBlock);
  byte highByte = SPI.transfer(controlByte);
  byte lowByte = SPI.transfer(0x00);
  digitalWrite(csPin, HIGH);
  SPI.endTransaction();
  return ((highByte & 0x0F) << 8) | lowByte;
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  delay(500);  // 시리얼 연결 대기 (while(!Serial) 제거)

  Serial.println("\n=== SYSTEM START ===");

  pinMode(MCP_CS_1, OUTPUT);
  pinMode(MCP_CS_2, OUTPUT);
  digitalWrite(MCP_CS_1, HIGH);
  digitalWrite(MCP_CS_2, HIGH);

  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(bmpCsPins[i], OUTPUT);
    digitalWrite(bmpCsPins[i], HIGH);
  }
  delay(10);

  SPI.begin();
  delay(100);  // SPI 버스 안정화 대기

  // BMP384 초기화: 천천히 순차 연결 + 실패 시 재시도 + 2차 시도
  Serial.println("BMP384 센서 초기화 중...");
  for (int i = 0; i < NUM_SENSORS; i++) {
    bool ok = false;
    for (int attempt = 0; attempt < 10; attempt++) {  // 5회 -> 10회 재시도
      if (pressureSensors[i].beginSPI(bmpCsPins[i], bmpClockFrequency) == BMP3_OK) {
        ok = true;
        break;
      }
      delay(50);  // 5ms -> 50ms: 전원/버스 안정화 대기
    }
    sensorOk[i] = ok;
    if (ok) {
      Serial.print("  BMP384 ");
      Serial.print(i);
      Serial.println(" OK");
    } else {
      Serial.print("  BMP384 ");
      Serial.print(i);
      Serial.println(" 1차 실패 (2차 시도 예정)");
    }
    delay(30);  // 센서 간 초기화 딜레이 (전원 분산)
  }

  // 실패한 센서 2차 시도 (다른 센서 초기화 후 버스/전원 안정)
  Serial.println("실패 센서 2차 연결 시도...");
  delay(200);  // 전체 센서 초기화 후 안정화
  for (int i = 0; i < NUM_SENSORS; i++) {
    if (sensorOk[i]) continue;
    bool ok = false;
    for (int attempt = 0; attempt < 15; attempt++) {  // 2차는 더 많이 시도
      if (pressureSensors[i].beginSPI(bmpCsPins[i], bmpClockFrequency) == BMP3_OK) {
        ok = true;
        break;
      }
      delay(100);  // 2차는 더 긴 대기
    }
    sensorOk[i] = ok;
    if (ok) {
      Serial.print("  BMP384 ");
      Serial.print(i);
      Serial.println(" 2차 OK");
    } else {
      Serial.print("  BMP384 ");
      Serial.print(i);
      Serial.println(" 최종 건너뜀");
    }
    delay(30);
  }

  // 오프셋 측정 (천천히)
  Serial.println("오프셋 측정 중...");
  for (int i = 0; i < NUM_SENSORS; i++) {
    if (!sensorOk[i]) {
      offset[i] = 0;
      continue;
    }
    bmp3_data data;
    int8_t err = pressureSensors[i].getSensorData(&data);
    delay(2);
    if (err == BMP3_OK) {
      offset[i] = data.pressure;
    } else {
      sensorOk[i] = false;
      Serial.print("  센서 ");
      Serial.print(i);
      Serial.println(" 오프셋 실패");
    }
    delay(5);  // 센서 간 측정 딜레이
  }

  Serial.println("=== SETUP COMPLETE ===");
  delay(500);
}

void loop() {
  // 1. Joint Data (MCP3208)
  for (int i = 0; i < 16; i++) {
    int csPin = (i < 8) ? MCP_CS_1 : MCP_CS_2;
    int rawVal = readMCP3208(csPin, i % 8);
    long targetVal = map((long)rawVal, IN_START[i], IN_END[i], OUT_START[i], OUT_END[i]);
    
    // Constrain
    if (i == 4 || i == 8 || i == 12) targetVal = constrain(targetVal, -1000, 1000);
    else if (i == 1) targetVal = constrain(targetVal, -4096, 4096);
    else targetVal = constrain(targetVal, 0, 4096);

    Serial.print(targetVal);
    Serial.print(",");
  }

  // 2. Tactile Data (BMP384, 기준값 대비 상대 압력) + 런타임 재연결
  unsigned long now = millis();
  int reconnectedSensor = -1;
  for (int i = 0; i < NUM_SENSORS; i++) {
    double pres = 0.0;
    if (sensorOk[i]) {
      bmp3_data data;
      int8_t err = pressureSensors[i].getSensorData(&data);
      if (err == BMP3_OK) {
        pres = data.pressure - offset[i];
        sensorFailCount[i] = 0;
      } else {
        sensorFailCount[i]++;
        // 연속 실패 시 재연결 시도
        if (sensorFailCount[i] >= FAIL_THRESHOLD &&
            (now - lastReconnectAttempt[i]) > RECONNECT_INTERVAL) {
          lastReconnectAttempt[i] = now;
          for (int a = 0; a < 5; a++) {
            if (pressureSensors[i].beginSPI(bmpCsPins[i], bmpClockFrequency) == BMP3_OK) {
              bmp3_data d;
              if (pressureSensors[i].getSensorData(&d) == BMP3_OK) {
                offset[i] = d.pressure;
                pres = d.pressure - offset[i];
                sensorFailCount[i] = 0;
                reconnectedSensor = i;
                break;
              }
            }
            delay(50);
          }
          if (sensorFailCount[i] >= FAIL_THRESHOLD) sensorFailCount[i] = 0;  // 재시도 리셋
        }
      }
    }
    Serial.print(pres, 2);
    if (i < NUM_SENSORS - 1)
      Serial.print(",");
  }

  Serial.println();
  if (reconnectedSensor >= 0) {
    Serial.print("  [재연결] 센서 ");
    Serial.println(reconnectedSensor);
  }
  delay(20);
}