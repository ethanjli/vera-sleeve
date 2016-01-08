/*
 * Simple code to read out the pin value from the fluid pressure sensor.
 * Corresponds to prototype P1 of milestone A.
 * Use with the Arduino IDE's Serial Monitor or Serial Plotter.
 */

const int kSerialRate = 9600; // Rate of serial data
const int kPressurePin = A0; // Analog input pin for the pressure sensor's signal pin
const int kADCInterval = 2; // Delay between ADC readings to settle between readings

void setup() {
  // initialize serial communications
  Serial.begin(kSerialRate);
}

void loop() {
  int sensorValue = analogRead(kPressurePin);
  Serial.println(sensorValue);
  delay(kADCInterval);
}
