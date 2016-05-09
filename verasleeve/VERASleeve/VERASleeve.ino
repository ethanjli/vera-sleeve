/*
 * Simple code to move the linear servo.
 * Use with the Arduino IDE's Serial Monitor or Serial Plotter.
 */

#include <Servo.h>

Servo band1;
Servo band2;
Servo band3;

const int kBand1Pin = 9;
const int kBand2Pin = 10;
const int kBand3Pin = 11;
const int kInitializationDelay = 5000;
const int kCyclePeriod = 10000;
const int kDelayBetweenBands = 2000;
const int kFirstBandDutyInterval = 6500;
const int kServoMin = 50;
const int kServoMax = 130;
const int blinkPin = 13;

void setup() {
  // initialize servo
  band1.attach(kBand1Pin);
  band2.attach(kBand2Pin);
  band3.attach(kBand3Pin);
  pinMode(blinkPin, OUTPUT);
  digitalWrite(blinkPin, HIGH);
  band1.write(kServoMax);
  band2.write(kServoMax);
  band3.write(kServoMax);
  delay(kInitializationDelay / 2);
  digitalWrite(blinkPin, LOW);
  delay(kInitializationDelay / 2);
}

void loop() {
  digitalWrite(blinkPin, HIGH);
  band1.write(kServoMin);
  delay(kDelayBetweenBands);

  digitalWrite(blinkPin, LOW);
  band2.write(kServoMin);
  delay(kDelayBetweenBands);
  
  digitalWrite(blinkPin, HIGH);
  band3.write(kServoMin);
  delay(kFirstBandDutyInterval - 2 * kDelayBetweenBands);

  digitalWrite(blinkPin, LOW);
  band1.write(kServoMax);
  band2.write(kServoMax);
  band3.write(kServoMax);
  delay(kCyclePeriod - kFirstBandDutyInterval);
}
