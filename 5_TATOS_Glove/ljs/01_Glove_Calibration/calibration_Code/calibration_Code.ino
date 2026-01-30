// [캘리브레이션용 코드 - 수정됨]
// 12개의 아날로그 핀 설정 (A0 ~ A11 사용 가정)
const int potPins[12] = {A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11};
int rawValues[12];

void setup() {
  Serial.begin(115200); // 통신 속도 설정
}

void loop() {
  Serial.print("Raw: ");
  for (int i = 0; i < 12; i++) {
    // [수정 포인트] i를 따옴표 없이 써야 숫자가 나옵니다.
    Serial.print("A[");
    Serial.print(i); 
    Serial.print("]"); 
    
    rawValues[i] = analogRead(potPins[i]);
    Serial.print(rawValues[i]);
    Serial.print("\t"); // 탭으로 구분
  }
  Serial.println(); // 줄바꿈
  delay(100);
}