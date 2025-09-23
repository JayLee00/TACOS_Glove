#include <SPI.h>
#include "src/SparkFun_BMP384_Arduino_Library/src/SparkFunBMP384.h"

// 사용할 센서의 개수
#define NUM_SENSORS 21

// 회로도에 따른 Chip Select (CS) 핀 번호 배열
byte csPins[NUM_SENSORS] = {
    22, 23, 24, 25, 26, 27, 28,
    29, 30, 31, 32, 33, 34, 35,
    36, 37, 38, 39, 40, 41, 42
    };
uint32_t clockFrequency = 1000000; //1MHz

typedef struct __attribute__((packed)) {
    uint8_t  stx;        // 0xA5
    uint32_t t_us;       // micros()
    uint8_t  count;      // 21
    int16_t vals[21];   // 실제 데이터
} Packet;

Packet packet;

// 각 센서에 대한 BMP384 객체를 배열로 생성
BMP384 pressureSensors[NUM_SENSORS];

double offset[NUM_SENSORS] = {0};

uint64_t sum = 0;
uint32_t count = 0;
unsigned int avr = 0;

void setup()
{
    packet.stx = 0xA5;
    packet.count = 21;

    // 시리얼 통신 시작
    Serial.begin(115200);
    Serial.println("BMP384 Multi-Sensor Test (SparkFun Library)");

    for (int i=0; i <NUM_SENSORS; i++)
    {
        pinMode(csPins[i], OUTPUT);
        digitalWrite(csPins[i], HIGH); 
    }
    delay(10);
    // SPI 라이브러리 초기화
    SPI.begin();
        bmp3_data data;

    // 각 센서를 순서대로 초기화
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        // beginSPI 함수를 사용하여 각 센서를 해당 CS 핀과 함께 초기화
        if (pressureSensors[i].beginSPI(csPins[i],clockFrequency) != BMP3_OK)
        {
            delay(1);
        }
    }
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        // 센서 데이터를 저장할 구조체 생성
        bmp3_data data;

        // 센서에서 데이터 읽기 수행
        int8_t err = pressureSensors[i].getSensorData(&data);
        delay(1);
        // 데이터 수집 성공 여부 확인
        if (err == BMP3_OK)
        {
            offset[i] = data.pressure;
        }
        else
        {
            // offset[i] = 0;
            while (pressureSensors[i].beginSPI(csPins[i],clockFrequency) != BMP3_OK)
            {
                delay(1);
            }
            i--;
            continue;
        }
    }
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        Serial.print(offset[i]);
        Serial.print("\t");
    }
    // while(1);
}

void loop()
{
    // 7개의 센서에서 순차적으로 데이터 읽기
    packet.t_us = micros();
    unsigned long bf_tim = micros();
    delay(1);
    unsigned long af_tim = micros() - bf_tim;
    Serial.print(af_tim);
    Serial.print("\t");

    bf_tim = micros();
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        // 센서 데이터를 저장할 구조체 생성
        bmp3_data data;
        // 센서에서 데이터 읽기 수행
        int8_t err = pressureSensors[i].getSensorData(&data);
        //delay(1);
        // 데이터 수집 성공 여부 확인
        if (err == BMP3_OK)
        {
            packet.vals[i] = (int16_t)((data.pressure - offset[i]) / 10);
        }
        else
        {
            packet.vals[i] = -1;
        }
    }
    af_tim = micros() - bf_tim;
    Serial.print(af_tim);
    Serial.print("\t");

    sum += af_tim;
    count++;

    avr = sum / count;
    Serial.print(avr);
    Serial.print("\t");

    
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        Serial.print(packet.vals[i]);
        Serial.print("\t");
    }
    Serial.print("\n");

    delay(1);
    // memcpy(packet.vals, value, sizeof(value));
    // Serial.write((uint8_t*)&packet, sizeof(packet));
}
