/*
 * Simple code to move the linear servo.
 * Use with the Arduino IDE's Serial Monitor or Serial Plotter.
 */

#include <Servo.h>

Servo testServo;
Servo testServo2;
Servo testServo3;

const int kSerialRate = 9600; // Rate of serial data
const int kServoPin = 12; // Spektrum servo output pin
const int kServo2Pin = 11; // Spektrum reversed servo output pin
const int kServo3Pin = 10; // Firgelli servo output pin
const int kAdjustmentInterval = 3000; // Delay between ADC readings to settle between reading
const int kServoMin = 55;
const int kServoMax = 130;
const int kServo3Min = 35;
const int kServo3Max = 170;

void setup() {
  // initialize serial communications
  Serial.begin(kSerialRate);
  // initialize servo
  testServo.attach(kServoPin);
  testServo2.attach(kServo2Pin);
  testServo3.attach(kServo3Pin);
}

void loop() {
  testServo.write(kServoMin);
  testServo2.write(kServoMax);
  testServo3.write(kServo3Max);
  delay(kAdjustmentInterval);
  testServo.write(kServoMax);
  testServo2.write(kServoMin);
  testServo3.write(kServo3Min);
  delay(kAdjustmentInterval);
}
