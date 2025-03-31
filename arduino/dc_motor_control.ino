// 🔧 DCモーターを制御するためのArduinoスケッチ
// このコードは、PWM信号を使用してDCモーターの回転方向と速度を制御します。

#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

const int dcMotors[] = {16,17};
const int mot_channels[] = {0};
const int mot_freq = 10000;
const int mot_res = 10;

void setup() {  
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); 

  Serial.begin(115200);

  // init motor
  pinMode(dcMotors[0], OUTPUT);
  ledcAttachPin(dcMotors[1], mot_channels[0]);
  ledcSetup(mot_channels[0], mot_freq, mot_res);
  
  // go forward, 
  digitalWrite(dcMotors[0], HIGH);

  // speed up
  for(int spd=1023;spd>=0;spd--) {
    Serial.println(spd);
    ledcWrite(mot_channels[0], spd);  
    delay(10);
  }

  delay(1000);

  // stop motor
  digitalWrite(dcMotors[0], LOW);
  ledcWrite(mot_channels[0], 0);
}

void loop() {
  
}
