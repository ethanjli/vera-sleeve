#!/usr/bin/env python3
"""Tests the fluid sensor."""
# Python imports
import time

# Package imports
from .. import leg

def stream():
    """Continuously prints the pin value on the fluid pressure sensor."""
    leg_test = leg.Leg()

    while True:
        print(leg_test.get_fluid_pressure_sensor())
        time.sleep(0.005)

if __name__ == "__main__":
    stream()
