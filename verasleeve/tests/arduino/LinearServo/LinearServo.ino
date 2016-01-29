/*
 * Simple code to move the linear servo.
 * Use with the Arduino IDE's Serial Monitor or Serial Plotter.
 */

 #include <Servo.h>

 Servo testServo;
 Servo testServo2;
 int servoPosition = 0;
 int servo2Position = 0;

const int kSerialRate = 9600; // Rate of serial data
const int kServoPin = 12; // Servo output pin
const int kServo2Pin = 11; // Servo output pin
const int kAdjustmentInterval = 50; // Delay between ADC readings to settle between readings
const int kServoStep = 1; // Servo adjustment distance
const int kServoMin = 55;
const int kServoMax = 130;

void setup() {
  // initialize serial communications
  Serial.begin(kSerialRate);
  // initialize servo
  testServo.attach(kServoPin);
  testServo2.attach(kServo2Pin);
}

void loop() {
  servo2Position = kServoMax;
  for (servoPosition = kServoMin; servoPosition <= kServoMax; servoPosition += kServoStep) {
    testServo.write(servoPosition);
    testServo2.write(servo2Position);
    servo2Position -= kServoStep;
    Serial.println(servoPosition);
  delay(kAdjustmentInterval);
  }
  servo2Position = kServoMin;
  for (servoPosition = kServoMax; servoPosition >= kServoMin; servoPosition -= kServoStep) {
    testServo.write(servoPosition);
    testServo2.write(servo2Position);
    servo2Position += kServoStep;
    Serial.println(servoPosition);
  delay(kAdjustmentInterval);
  }
}
