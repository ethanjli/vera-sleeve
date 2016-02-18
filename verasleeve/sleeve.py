"""Controls the Arduino board of the leg model test fixture and contractile sleeve."""
# Python imports
import time

# Dependency imports
import nanpy
from nanpy.watchdog import Watchdog
from serial.serialutil import SerialException
import pykka

# Package imports
from verasleeve import actors

# Device parameters
# These are servo motor pins
BAND_SERVO_PINS = [12, 11, 10]
NUM_BANDS = len(BAND_SERVO_PINS)
BAND_SERVO_IDS = list(range(NUM_BANDS))

class SleeveServos(object):
    """Models the Arduino controller of the leg sleeve."""
    def __init__(self, connection=None):
        super().__init__()
        if connection is None:
            try:
                connection = nanpy.SerialManager()
            except SerialException:
                raise RuntimeError("Could not connect to the Arduino!") from None
        self.__connection = connection
        self.__band_servos = [nanpy.Servo(servo_pin, connection)
                              for servo_pin in BAND_SERVO_PINS]

    def set_servo_position(self, servo_id, position):
        """Changes the position of the specified servo."""
        self.__band_servos[servo_id].write(position)

    def quit(self):
        """Resets the Arduino.
        Must be called when the program exits to reset the servos, or else the Arduino must be
        manually reset. The consequence of not doing this is that the Arduino will not drive the
        servos correctly. Invalidates all objects on an existing Arduino connection.
        """
        watchdog = Watchdog(self.__connection)
        watchdog.enable(0)
        time.sleep(0.2)
