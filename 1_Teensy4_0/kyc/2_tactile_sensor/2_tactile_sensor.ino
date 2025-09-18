#include <SPI.h>
#include "SparkFunBMP384.h" // SparkFun 라이브러리를 사용합니다.

// 사용할 센서의 개수
#define NUM_SENSORS 7 * 3
const uint8_t PIN_MISO = 12;      // 기본 MISO

// 회로도에 따른 Chip Select (CS) 핀 번호 배열
// CSB1~CSB7 -> D2, D3, D4, D5, D6, D7, D8
// byte csPins[NUM_SENSORS] = {0,1,2,3,4,5,6,7,8,9,10,14,15,16};
//byte csPins[NUM_SENSORS] = {7,8,9,10,14,15,16};
// byte csPins[NUM_SENSORS] = {17,18,19,20,21,22,23};
byte csPins[NUM_SENSORS] = { 0,  1,  2,  3,  4,  5,  6,
                             7,  8,  9, 10, 14, 15, 16,
                            17, 18, 19, 20, 21, 22, 23};
// byte csPins[NUM_SENSORS] = {0,1,2,3,4,5,6,7};
uint32_t clockFrequency = 1000000;
//10000, 900 000 ==> 933.8kHz
//1000 000 ==> 1MHz
//10 000 000 ==> 10MHz
//100 000 000 ==> 80MHz, X
//50 000 000 ==> 47.9MHz, X
// SPISettings settingA(1000000, MSBFIRST,SPI_MODE2);

// 각 센서에 대한 BMP384 객체를 배열로 생성
BMP384 pressureSensors[NUM_SENSORS];

void setup()
{
    delay(100);
    for (int i = 0; i < NUM_SENSORS; ++i) {
        // if(csPins[i] == 17 || csPins[i] == 18 || csPins[i] == 19 || csPins[i] == 21 || csPins[i] == 22 || csPins[i] == 23)
        // {
        //     pinMode(csPins[i], INPUT);
        //     continue;
        // }
        pinMode(csPins[i], OUTPUT);
        digitalWriteFast(csPins[i], HIGH); // 비선택 상태 강제
    }
    delay(50);
    //  for (int i=0; i <11; i++)
    //  {
    
    //    pinMode(i, OUTPUT); // 출력 모드 10 설정
    //    digitalWrite(i, HIGH); 
    //  }

    //      for (int i=14; i <24; i++)
    //  {
    
    //    pinMode(i, OUTPUT); // 출력 모드 10 설정
    //    digitalWrite(i, HIGH); 
    //  }
    // delay(100);

    
    // 각 센서를 순서대로 초기화
//     for (int i = 0; i < NUM_SENSORS; i++)
//     {
//         Serial.printf("Initializing Sensor %d (CS=%d)... ", i+1, csPins[i]);
        
//         // beginSPI 함수를 사용하여 각 센서를 해당 CS 핀과 함께 초기화
//         if (pressureSensors[i].beginSPI(csPins[i], clockFrequency) != BMP3_OK)
//         {
//             // 연결 실패 시 메시지 출력
//             Serial.printf("Error: BMP384 not connected on CS %d\n", csPins[i]);
//            // while (1); // 에러 발생 시 프로그램 정지
//             delay(10);
//         } else {
//         Serial.println("Done.");
//         }
//         delay(20);
//     }
//     Serial.println("\nAll sensors initialized successfully!");

    // 시리얼 통신 시작
    Serial.begin(115200);
    Serial.println("BMP384 Multi-Sensor Test (SparkFun Library)");
    delay(100);
    int j = 0;
    for (int i = 0; i < NUM_SENSORS; i++) {
    // SPI 라이브러리 초기화
    // pinMode(PIN_MISO, INPUT_PULLDOWN); // SPI.begin() 전에 호출
    // delay(50);
    SPI.begin();
    delay(50);
        //Serial.printf("Initializing %d (CS=%d)... ", i+1, csPins[i]);
        // if(csPins[i] == 16 || csPins[i] == 17 || csPins[i] == 18 || csPins[i] == 19 || csPins[i] == 21)
        // {
        //     Serial.println("NOW!!!!!");
        //     delay(5000);
        // }
        // if(csPins[i] == 17 || csPins[i] == 18 || csPins[i] == 19 || csPins[i] == 21 || csPins[i] == 22 || csPins[i] == 23 || csPins[i] == 20)
        // {
        //     continue;
        // }
        //digitalWriteFast(csPins[i], LOW);
        int8_t rc = pressureSensors[i].beginSPI(csPins[i], clockFrequency);
        // asm volatile("nop; nop; nop;");

        // ★ 무조건 deassert: begin 경로가 어디서 실패해도 HIGH 보장
        digitalWriteFast(csPins[i], HIGH);
        //delay(10);


        if (rc != BMP3_OK) {
            Serial.printf("FAIL rc=%d on CS %d\n", rc, csPins[i]);
            digitalWriteFast(csPins[i], HIGH);
            delay(10);
            // if(csPins[i] == 16 || csPins[i] == 17 || csPins[i] == 18 || csPins[i] == 19)
            //     continue;
            i--;

            j++;
            if(j>=10) {
                i++;
                j = 0;
            }
            continue;
        } else {
            Serial.println("OK");
        }
        delay(10);
    }
    // ★ 전체 초기화 끝나고 한 번 더 모든 CS 정리
    // for (int i = 0; i < NUM_SENSORS; ++i) {
    // pinMode(csPins[i], OUTPUT);
    // digitalWriteFast(csPins[i], HIGH);
    // }
    Serial.print("\n\n");
}

void loop()
{
    // 7개의 센서에서 순차적으로 데이터 읽기
    Serial.println("------------------------------------");
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        // if(csPins[i] == 17 || csPins[i] == 18 || csPins[i] == 19 || csPins[i] == 21 || csPins[i] == 22 || csPins[i] == 23 || csPins[i] == 20)
        // {
        //     continue;
        // }
        // 센서 데이터를 저장할 구조체 생성
        bmp3_data data;

        // 센서에서 데이터 읽기 수행
        int8_t err = pressureSensors[i].getSensorData(&data);
        delay(2);
        // 데이터 수집 성공 여부 확인
        if (err == BMP3_OK)
        {
            // 성공 시, 센서 번호와 함께 온도/압력 값 출력
            Serial.print("Sensor ");
            Serial.print(i + 1);
            Serial.print(": ");

            // 압력 값 출력 (Pa 단위를 hPa로 변환)
            Serial.print(data.pressure / 100.0);
            Serial.print(" hPa");

            Serial.print("\t| "); // 탭으로 구분

            // 온도 값 출력
            Serial.print(data.temperature);
            Serial.println(" *C");
        }
        else
        {
            // 실패 시, 에러 메시지 출력
            Serial.print("Error getting data from Sensor ");
            Serial.print(i + 1);
            Serial.print("! Error code: ");
            Serial.println(err);
        }
        delay(2); // 센서 간 짧은 여유
    }
    // 초마다 모든 센서 값을 새로고침
    delay(500);
}