#include <SPI.h>

const int CS_1 = 46;
const int CS_2 = 47;

void setup() {
  Serial.begin(115200);
  SPI.begin();
  
  pinMode(CS_1, OUTPUT);
  pinMode(CS_2, OUTPUT);
  digitalWrite(CS_1, HIGH);
  digitalWrite(CS_2, HIGH);
}

// CS 핀번호와 채널을 인자로 받는 통합 함수
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

float filteredValues[16] = {0,}; // 8개가 아니라 16개로 확장
float alpha = 0.1;

void loop() {
  // CS_1 읽기 (0~7)
  for (int i = 0; i < 8; i++) {
    int rawVal = readMCP3208(CS_1, i);
    filteredValues[i] = (alpha * rawVal) + ((1.0 - alpha) * filteredValues[i]);
    
    Serial.print(i); Serial.print(":");
    Serial.print((int)filteredValues[i]); Serial.print("\t");
  }

  // CS_2 읽기 (8~15)
  for (int i = 0; i < 8; i++) {
    int rawVal = readMCP3208(CS_2, i);
    // 인덱스를 i+8로 지정하여 별도의 공간에 저장
    filteredValues[i + 8] = (alpha * rawVal) + ((1.0 - alpha) * filteredValues[i + 8]);
    
    Serial.print(i + 8); Serial.print(":");
    Serial.print((int)filteredValues[i + 8]); Serial.print("\t");
  }
  Serial.println();
  delay(10);
}
