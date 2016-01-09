#!/usr/bin/env python3
"""Tests the connection to the Arduino over nanpy."""
# Python imports
from time import sleep

# Package imports
import nanpy

def blink():
    """Connects to the Arduino and blinks the LED on pin 13."""
    connection = nanpy.SerialManager()
    board = nanpy.ArduinoApi(connection=connection)
    board.pinMode(13, board.OUTPUT)

    while True:
        board.digitalWrite(13, board.HIGH)
        sleep(1.0)
        board.digitalWrite(13, board.LOW)
        sleep(1.0)

if __name__ == "__main__":
    blink()
