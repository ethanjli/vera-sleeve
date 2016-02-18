#!/usr/bin/env python3
"""Tests the connection to the Arduino over nanpy."""
# Python imports
from time import sleep
import logging

# Package imports
from .. import sleeve

logging.basicConfig(level=logging.INFO)

def control():
    """Connects to the Arduino and moves the servos on the leg sleeve."""
    servos = sleeve.SleeveServos()

    for _ in range(2):
        servos.set_servo_position(0, 50)
        servos.set_servo_position(1, 130)
        servos.set_servo_position(2, 130)
        sleep(1.5)
        servos.set_servo_position(0, 50)
        servos.set_servo_position(1, 50)
        servos.set_servo_position(2, 130)
        sleep(1.5)
        servos.set_servo_position(0, 130)
        servos.set_servo_position(1, 50)
        servos.set_servo_position(2, 50)
        sleep(1.5)
        servos.set_servo_position(0, 130)
        servos.set_servo_position(1, 130)
        servos.set_servo_position(2, 50)
        sleep(1.5)
        servos.set_servo_position(0, 130)
        servos.set_servo_position(1, 130)
        servos.set_servo_position(2, 130)
        sleep(1.5)

    servos.quit()

if __name__ == "__main__":
    control()
