#include <SPI.h>

// ==========================================
// KISTAR Hand - Raw Data Filter Check
// ==========================================

const int CS_PIN = 2;

const int POT_PINS[12] = {
  A3, A2, A1, A0,   
  A7, A6, A5, A4,   
  A11, A10, A9, A8  
};

// [필터 설정]
// MCP3208 채널 4개(CH0~CH3)의 필터 값을 저장할 배열
float mcpFiltered[4] = {0, 0, 0, 0}; 

// 필터 강도 (0.01 ~ 1.0)
// 0.1: 매우 부드러움 (노이즈 제거 탁월, 반응 약간 느림)
// 0.2: 적당함
// 1.0: 필터 없음
float alpha = 0.3; 

// (주석 처리된 배열들은 그대로 두었습니다)
// const int IN_START[16] = { ... };
// const int IN_END[16] = { ... };
// const int OUT_START[16] = { ... };
// const int OUT_END[16] = { ... };

void setup() {
  Serial.begin(115200);
  
  pinMode(CS_PIN, OUTPUT);
  digitalWrite(CS_PIN, HIGH);
  SPI.begin();
  
  // SPI 속도 안정화 (1MHz)
  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
}

int readMCP3208(int channel) {
  if (channel > 7 || channel < 0) return -1;
  digitalWrite(CS_PIN, LOW);
  byte byte1 = 0b00000110 | ((channel & 0x04) >> 2);
  byte byte2 = (channel & 0x03) << 6;
  SPI.transfer(byte1);
  byte result1 = SPI.transfer(byte2);
  byte result2 = SPI.transfer(0x00);
  digitalWrite(CS_PIN, HIGH);
  return ((result1 & 0x0F) << 8) | result2;
}

void loop() {
  // 매핑 루프는 주석 처리된 상태 그대로 둠 (구조만 유지)
  for (int i = 0; i < 16; i++) {
    // ...
  }

  // ==========================================
  // [여기서부터 필터 테스트]
  // ==========================================
  
  // 1. 아두이노 값 읽기 (비교용)
  int arduinoRaw = analogRead(POT_PINS[9]); 

  // 2. MCP3208 (CH0) 값 읽기
  int mcpRaw = readMCP3208(0);

  // 3. [필터 적용]
  // 초기값이 0이면 현재 값으로 바로 세팅 (튀는 현상 방지)
  if (mcpFiltered[0] == 0) mcpFiltered[0] = mcpRaw;

  // 이동 평균 필터 공식: (이전값 * 0.9) + (현재값 * 0.1)
  mcpFiltered[0] = (mcpFiltered[0] * (1.0 - alpha)) + (mcpRaw * alpha);


  // 4. 결과 출력
  // 포맷: "아두이노(참고) | MCP(날것) -> MCP(필터됨)"

  Serial.print(arduinoRaw);
  Serial.print(", ");
  Serial.print(mcpRaw); // 노이즈로 튀는 값
  Serial.print(", ");
  Serial.println((int)mcpFiltered[0]); // 차분해진 값
  
  delay(5);
}