void setup() {
  Serial.begin(9600);
}

void loop() {
  // 0번부터 3번까지 아날로그 핀의 값을 읽어옵니다.
  int sensorValues[12];
  for (int i = 0; i < 12; i++) {
    sensorValues[i] = analogRead(A0 + i);
  }

  // 읽어온 값을 시리얼 모니터에 출력합니다.
  Serial.print("[");  // 배열 시작 괄호

  for (int i = 0; i < 16; i++) {
    if (i < 12) {
      Serial.print(sensorValues[i]);
      Serial.print(" ");
    } else
      Serial.print("0");
      Serial.print(" ");

        // 마지막 값이 아니면 쉼표와 공백을 출력합니다.

  }


Serial.println("]");  // 배열 끝 괄호 및 줄바꿈

delay(100);
}