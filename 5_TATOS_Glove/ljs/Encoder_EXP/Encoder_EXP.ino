void setup() {
  Serial.begin(9600);
}

void loop() {
  // 0번부터 3번까지 아날로그 핀의 값을 읽어옵니다.
  int sensorValues[1];
    sensorValues[1] = analogRead(A0);

  // 읽어온 값을 시리얼 모니터에 출력합니다.
    Serial.println(sensorValues[1]);
  
  // Serial.println(""); // 구분선 출력

  delay(500); // 0.1초 대기
}