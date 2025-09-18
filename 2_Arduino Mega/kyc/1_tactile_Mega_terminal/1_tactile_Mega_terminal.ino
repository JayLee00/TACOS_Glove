#include <SPI.h>
#include "src/SparkFun_BMP384_Arduino_Library/src/SparkFunBMP384.h"

// 사용할 센서의 개수
#define NUM_SENSORS 21

// 회로도에 따른 Chip Select (CS) 핀 번호 배열
byte csPins[NUM_SENSORS] = {22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42};
uint32_t clockFrequency = 1000000; //1MHz

// 각 센서에 대한 BMP384 객체를 배열로 생성
BMP384 pressureSensors[NUM_SENSORS];

void setup()
{
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

    // 각 센서를 순서대로 초기화
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        Serial.print("Initializing Sensor ");
        Serial.print(i + 1);
        Serial.print("... ");
        
        // beginSPI 함수를 사용하여 각 센서를 해당 CS 핀과 함께 초기화
        if (pressureSensors[i].beginSPI(csPins[i],clockFrequency) != BMP3_OK)
        {
            // 연결 실패 시 메시지 출력
            Serial.print("Error: BMP384 not connected, check wiring on CS pin ");
            Serial.println(csPins[i]);
           // while (1); // 에러 발생 시 프로그램 정지
            delay(1);
        }
        Serial.println("Done.");
    }
    Serial.println("\nAll sensors initialized successfully!");
}

void loop()
{
    // 7개의 센서에서 순차적으로 데이터 읽기
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        // 센서 데이터를 저장할 구조체 생성
        bmp3_data data;

        // 센서에서 데이터 읽기 수행
        int8_t err = pressureSensors[i].getSensorData(&data);
        delay(1);
        // 데이터 수집 성공 여부 확인
        if (err == BMP3_OK)
        {   //성공 시, 센서 번호와 함께 온도/압력 값 출력
            // Serial.print("Sensor ");
            Serial.print(i + 1);
            Serial.print(": ");
            // Raw 압력 값 출력
            // Serial.print("Raw P: ");
            Serial.print(data.pressure);//double
            Serial.print("\t| "); // 탭으로 구분
            // Raw 온도 값 출력
            // Serial.print("Raw T: ");
            // Serial.println(data.temperature);
        }
        else
        {
            // 실패 시, 에러 메시지 출력
            Serial.print("Error getting data from Sensor ");
            Serial.print(i + 1);
            Serial.print("! Error code: ");
            Serial.println(err);
        }
    }
    Serial.print("\r");
    // Serial.println("------------------------------------");
    // 1초마다 모든 센서 값을 새로고침
    delay(10);
}
