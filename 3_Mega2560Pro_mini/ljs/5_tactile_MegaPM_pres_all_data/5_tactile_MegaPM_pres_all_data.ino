#include <SPI.h>
#include "src/SparkFun_BMP384_Arduino_Library/src/SparkFunBMP384.h"

/*************** 설정 ***************/
// 트러블슈팅: 115200으로 먼저 시도. 됐으면 1000000으로 변경
#define SERIAL_BAUD 115200
#define DEBUG_MODE 1   // 1=디버그 출력, 0=배열만 출력

#define NUM_SENSORS 21
// CS핀 8~28 (보드 변경 후)
byte csPins[NUM_SENSORS] = {
    8, 9, 10, 11, 12, 13, 14,
    15, 16, 17, 18, 19, 20, 21,
    22, 23, 24, 25, 26, 27, 28
};
uint32_t clockFrequency = 1000000;

BMP384 pressureSensors[NUM_SENSORS];
double offset[NUM_SENSORS] = {0};
bool sensorOk[NUM_SENSORS] = {false};  // 초기화 성공한 센서만 true

/*************************************/
/*************** setup ***************/
/*************************************/
void setup()
{
    Serial.begin(SERIAL_BAUD);
    delay(500);  // 시리얼 모니터 연결 대기

#if DEBUG_MODE
    Serial.println("--- [1] setup 시작 ---");
#endif

    for (int i = 0; i < NUM_SENSORS; i++)
    {
        pinMode(csPins[i], OUTPUT);
        digitalWrite(csPins[i], HIGH);
    }
    delay(10);

#if DEBUG_MODE
    Serial.println("--- [2] SPI 초기화 ---");
#endif
    SPI.begin();

#if DEBUG_MODE
    Serial.println("--- [3] 센서 beginSPI (실패 시 건너뜀) ---");
#endif
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        bool ok = false;
        for (int attempt = 0; attempt < 5; attempt++)
        {
            if (pressureSensors[i].beginSPI(csPins[i], clockFrequency) == BMP3_OK)
            {
                ok = true;
                break;
            }
            delay(5);
        }
        sensorOk[i] = ok;
#if DEBUG_MODE
        if (!ok) {
            Serial.print("  센서 ");
            Serial.print(i);
            Serial.print(" (CS핀 ");
            Serial.print(csPins[i]);
            Serial.println(") 건너뜀");
        }
#endif
    }

#if DEBUG_MODE
    Serial.println("--- [4] 오프셋 측정 ---");
#endif
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        if (!sensorOk[i]) {
            offset[i] = 0;
            continue;
        }
        bmp3_data data;
        int8_t err = pressureSensors[i].getSensorData(&data);
        delay(1);

        if (err == BMP3_OK)
        {
            offset[i] = data.pressure;
        }
        else
        {
#if DEBUG_MODE
            Serial.print("  센서 ");
            Serial.print(i);
            Serial.println(" getSensorData 실패, 해당 센서 비활성");
#endif
            sensorOk[i] = false;
        }
    }

#if DEBUG_MODE
    Serial.println("--- [5] setup 완료, loop 시작 ---");
#endif
}

/*************************************/
/*************** loop ****************/
/*************************************/
void loop()
{
    double pres[NUM_SENSORS];

    for (int i = 0; i < NUM_SENSORS; i++)
    {
        if (!sensorOk[i]) {
            pres[i] = 0.0;
            continue;
        }
        bmp3_data data;
        int8_t err = pressureSensors[i].getSensorData(&data);

        if (err == BMP3_OK)
            pres[i] = (data.pressure - offset[i]);
        else
            pres[i] = 0.0;
    }

    Serial.print("[");
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        Serial.print(pres[i], 2);
        if (i < NUM_SENSORS - 1)
            Serial.print(", ");
    }
    Serial.println("]");

    delay(20);
}
