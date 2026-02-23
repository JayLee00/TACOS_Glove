#include <SPI.h>
#include "src/SparkFun_BMP384_Arduino_Library/src/SparkFunBMP384.h"

/*************** 5_tactile_MegaPM_pres_all_data와 동일 설정 ***************/
#define SERIAL_BAUD 1000000UL      // 1 Mbps (동작 확인된 값)
#define NUM_SENSORS 21
uint32_t clockFrequency = 1000000;  // 1MHz

byte csPins[NUM_SENSORS] = {
    8, 9, 10, 11, 12, 13, 14,
    15, 16, 17, 18, 19, 20, 21,
    22, 23, 24, 25, 26, 27, 28
};

BMP384 pressureSensors[NUM_SENSORS];
double offset[NUM_SENSORS] = {0};

/*************************************/
/*************** setup ***************/
/*************************************/
void setup()
{
    Serial.begin(SERIAL_BAUD);
    while (!Serial) { /* optional */ }

    for (int i = 0; i < NUM_SENSORS; i++)
    {
        pinMode(csPins[i], OUTPUT);
        digitalWrite(csPins[i], HIGH);
    }
    delay(10);

    SPI.begin();

    // 각 센서를 순서대로 초기화 (5_tactile과 동일)
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        if (pressureSensors[i].beginSPI(csPins[i], clockFrequency) != BMP3_OK)
        {
            delay(1);
            i--;
        }
    }

    // 오프셋 측정 (5_tactile과 동일)
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        bmp3_data data;
        int8_t err = pressureSensors[i].getSensorData(&data);
        delay(1);

        if (err == BMP3_OK)
        {
            offset[i] = data.pressure;
        }
        else
        {
            while (pressureSensors[i].beginSPI(csPins[i], clockFrequency) != BMP3_OK)
            {
                delay(1);
            }
            delay(100);
            i--;
            continue;
        }
    }

    Serial.println("[BMP384 21ch Ready]");
}

/******************************************************/
/* Loop: [val1, val2, ..., val21] 배열 형식 출력       */
/******************************************************/
void loop()
{
    double pres[NUM_SENSORS];

    for (int i = 0; i < NUM_SENSORS; i++)
    {
        bmp3_data data;
        int8_t err = pressureSensors[i].getSensorData(&data);

        if (err == BMP3_OK)
            pres[i] = data.pressure - offset[i];  // Pa, 기준값 대비
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