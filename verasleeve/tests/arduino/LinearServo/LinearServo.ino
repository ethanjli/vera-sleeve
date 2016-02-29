/*
 * Simple code to move the linear servo.
 * Use with the Arduino IDE's Serial Monitor or Serial Plotter.
 */

#include <Servo.h>

Servo testServo;

const int kServoPin = 11; // Firgelli servo output pin
const int kAdjustmentInterval = 3000; // Delay between ADC readings to settle between reading
const int kServoMin = 50;
const int kServoMax = 130;
const int blinkPin = 13;

void setup() {
  // initialize servo
  testServo.attach(kServoPin);
  pinMode(blinkPin, OUTPUT);

}

void loop() {
  testServo.write(kServoMax);
  digitalWrite(blinkPin, HIGH);
  delay(kAdjustmentInterval / 4);
  digitalWrite(blinkPin, LOW);
  delay(kAdjustmentInterval / 4);
  digitalWrite(blinkPin, HIGH);
  delay(kAdjustmentInterval / 4);
  digitalWrite(blinkPin, LOW);
  delay(kAdjustmentInterval / 4);
  testServo.write(kServoMin);
  digitalWrite(blinkPin, HIGH);
  delay(kAdjustmentInterval / 4);
  digitalWrite(blinkPin, LOW);
  delay(kAdjustmentInterval / 4);
  digitalWrite(blinkPin, HIGH);
  delay(kAdjustmentInterval / 4);
  digitalWrite(blinkPin, LOW);
  delay(kAdjustmentInterval / 4);
}
