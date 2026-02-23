#include <SPI.h>

const int CS_1 = 46;
const int CS_2 = 44;

// 1. 입력 캘리브레이션 데이터 (ADC 값)
const int IN_START[16] = {
  2220, 2967, 2060, 2230, // Thumb (L0~3)
  2590, 2385, 2042, 1963, // Index (L4: -45도, L5~7)
  2625, 1744, 2317, 2112, // Middle (L8: -45도, L9~11)
  2170, 1607, 1736, 1985  // Ring (L12: -45도, L13~15)
};

const int IN_END[16] = {
  1130, 813, 3189, 1100, // Thumb (L0~3)
  1620, 1170, 960, 3096, // Index (L4: +45도, L5~7)
  1552, 874, 1194, 3205, // Middle (L8: +45도, L9~11)
  1103, 844, 608, 3143    // Ring (L12: +45도, L13~15)
};

// 2. 출력 타겟 데이터 (엔코더 값)
const int OUT_START[16] = {
  0, -4096, 0, 0,         // Thumb (L1은 -4096 시작)
  2048, 0, 0, 0,          // Index (L4는 +45도일 때 2048)
  2048, 0, 0, 0,          // Middle
  2048, 0, 0, 0           // Ring
};

const int OUT_END[16] = {
  4096, 4096, 4096, 4096, 
  -2048, 4096, 4096, 4096, // Index (L4는 -45도일 때 -2048)
  -2048, 4096, 4096, 4096, // Middle
  -2048, 4096, 4096, 4096  // Ring
};

// 필터 관련 변수
float filteredValues[16] = {0,}; 
float alpha = 0.02; // 0.1: 강한 필터링 (부드러움), 0.2: 빠른 반응

void setup() {
  Serial.begin(115200);
  SPI.begin();
  
  pinMode(CS_1, OUTPUT);
  pinMode(CS_2, OUTPUT);
  digitalWrite(CS_1, HIGH);
  digitalWrite(CS_2, HIGH);
}

int readMCP3208(int csPin, byte channel) {
  byte controlBlock = 0x06 | ((channel & 0x04) >> 2);
  byte controlByte = (channel & 0x03) << 6;

  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0)); 
  digitalWrite(csPin, LOW);
  SPI.transfer(controlBlock);
  byte highByte = SPI.transfer(controlByte);
  byte lowByte = SPI.transfer(0x00);
  digitalWrite(csPin, HIGH);
  SPI.endTransaction();

  return ((highByte & 0x0F) << 8) | lowByte;
}

void loop() {
  for (int i = 0; i < 16; i++) {
    // 1. 칩 선택 및 데이터 읽기
    int csPin = (i < 8) ? CS_1 : CS_2;
    int rawVal = readMCP3208(csPin, i % 8);
    
    // 2. EMA 필터 적용
    // filteredValues[i] = (alpha * rawVal) + ((1.0 - alpha) * filteredValues[i]);
    filteredValues[i] = rawVal;
    // 3. 선형 매핑 (Targeting)
    long targetVal = map((long)filteredValues[i], IN_START[i], IN_END[i], OUT_START[i], OUT_END[i]);
    
    // 4. 관절별 가동범위 제한 (Constrain)
    if (i == 4 || i == 8 || i == 12) {
      // Spread 관절: 실제 로봇 한계인 +-15도(-683 ~ 683)로 제한
      targetVal = constrain(targetVal, -1000, 1000);
    } else if (i == 1) {
      // Thumb Rotation: -4096 ~ 4096
      targetVal = constrain(targetVal, -4096, 4096);
    } else {
      // 일반 Flexion 관절: 0 ~ 4096
      targetVal = constrain(targetVal, 0, 4096);
    }
    
// --- ROS 2용 출력 형식 수정 ---
    Serial.print(targetVal); // 숫자만 출력
    if (i < 15) {
      Serial.print(","); // 마지막 데이터 전까지만 쉼표 출력
    }
  }
  
  Serial.println(); // 한 줄의 끝 (파이썬의 readline() 인식 지점)
  delay(5); // 100Hz 주기로 전송
  }
