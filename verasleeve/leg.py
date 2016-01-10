"""Controls the Arduino board of the leg model test fixture."""
# Dependency imports
import nanpy

# Device parameters
FLUID_SENSOR_PORT = 'A0'

class Leg(object):
    """Models the Arduino controller of the leg model test fixture."""
    def __init__(self):
        super().__init__()
        connection = nanpy.SerialManager()
        self._board = nanpy.ArduinoApi(connection=connection)

    def get_fluid_pressure_sensor(self):
        return self._board.analogRead(FLUID_SENSOR_PORT)
