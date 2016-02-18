#!/usr/bin/env python3
"""Tests the connection to the Arduino over nanpy."""
# Python imports
from time import sleep

# Package imports
import nanpy

def control():
    """Connects to the Arduino and moves the servo on pin 12."""
    connection = nanpy.SerialManager()
    servo = nanpy.Servo(12, connection)

    while True:
        servo.write(50)
        sleep(4.0)
        servo.write(130)
        sleep(4.0)

if __name__ == "__main__":
    control()
