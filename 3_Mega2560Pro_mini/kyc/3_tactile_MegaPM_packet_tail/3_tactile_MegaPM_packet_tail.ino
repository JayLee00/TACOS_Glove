#include <SPI.h>
#include "src/SparkFun_BMP384_Arduino_Library/src/SparkFunBMP384.h"

/*************** Timer Setting ***************/
#define SERIAL_BAUD 1000000UL      // 1 Mbps (16 MHz에서 오차 0%)
#define OCR2A_VALUE 173            // 16MHz / (1024*(1+173)) ≈ 89.799 Hz
// Timer2 prescaler = 1024  → CS22=1, CS21=1, CS20=1
#define TIMER2_PRESC_BITS ((1<<CS22)|(1<<CS21)|(1<<CS20))

/*************** Sensors ***************/
// 사용할 센서의 개수
#define NUM_SENSORS 21

// 회로도에 따른 Chip Select (CS) 핀 번호 배열
byte csPins[NUM_SENSORS] = {
    22, 23, 24, 25, 26, 27, 28,
    29, 30, 31, 32, 33, 34, 35,
    36, 37, 38, 39, 40, 41, 42
    };
uint32_t clockFrequency = 1000000; //1MHz

// 각 센서에 대한 BMP384 객체를 배열로 생성
BMP384 pressureSensors[NUM_SENSORS];
double offset[NUM_SENSORS] = {0};

/*************** Packet ***************/
typedef struct __attribute__((packed)) {
    uint8_t  stx;        // 0xA5
    uint32_t t_us;       // micros() count로 변경
    uint8_t  size;      // 패킷 사이즈
    int16_t vals[21];   // 실제 데이터
    uint8_t  etx;//0x5A
} Packet;
//만약 packed가 없으면 t_us 정렬 때문에 stx 뒤에 패딩이 들어가 sizeof가 49를 초과할 수 있음
Packet packet;

/*************** Timer ***************/
volatile bool tick_90hz = false;

ISR(TIMER2_COMPA_vect) {
  tick_90hz = true;
}

void timer2_start_ctc_90hz() {
  cli();
  // 카운터/제어 레지스터 초기화
  TCCR2A = 0;
  TCCR2B = 0;
  TCNT2  = 0;
  // CTC 모드: WGM21=1 (WGM20=0, WGM22=0)
  TCCR2A |= (1 << WGM21);
  // 비교일치 값
  OCR2A = OCR2A_VALUE;
  // 분주비 1024
  TCCR2B |= TIMER2_PRESC_BITS;
  // 비교일치 A 인터럽트 허용
  TIMSK2 |= (1 << OCIE2A);
  sei();
}

/*************************************/
/*************** setup ***************/
/*************************************/
void setup()
{
    packet.stx = 0xA5;
    packet.etx = 0x5A;

    // 시리얼 통신 시작
    Serial.begin(SERIAL_BAUD);
    while (!Serial) { /* optional */ }
    // Serial.println("BMP384 Multi-Sensor");

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
        // beginSPI 함수를 사용하여 각 센서를 해당 CS 핀과 함께 초기화
        if (pressureSensors[i].beginSPI(csPins[i],clockFrequency) != BMP3_OK)
        {
            delay(1);
            // Serial.println(i);
            i--;
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
            delay(100);
            i--;
            continue;
        }
    }
    
    timer2_start_ctc_90hz();
}

uint64_t sum = 0;
uint32_t count = 0;
unsigned int avr = 0;

/*************************************/
/*************** loop ****************/
/*************************************/
void loop()
{
    // 7개의 센서에서 순차적으로 데이터 읽기
    packet.t_us = micros();
    for (int i = 0; i < NUM_SENSORS; i++)
    {
        // 센서 데이터를 저장할 구조체 생성
        bmp3_data data;
        // 센서에서 데이터 읽기 수행
        int8_t err = pressureSensors[i].getSensorData(&data);
        // delay(1);
        // 데이터 수집 성공 여부 확인
        if (err == BMP3_OK)
        {
            packet.vals[i] = (int16_t)((data.pressure - offset[i]) / 10);
        }
        else
        {
            packet.vals[i] = 0;
        }
    }
    packet.size = sizeof(Packet); //STX/ETX 포함 크기
    if (tick_90hz) {
        tick_90hz = false;
        Serial.write((uint8_t*)&packet, sizeof(packet));
    }
    // uint32_t delay_time = micros() - packet.t_us;
    // Serial.print(delay_time);
    // Serial.print("\t");
    // sum += delay_time;
    // count++;

    // avr = sum / count;
    // Serial.println(avr);
}
