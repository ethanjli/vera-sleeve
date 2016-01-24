"""Controls the Arduino board of the leg model test fixture."""
# Python imports
import time

# Dependency imports
import nanpy
from serial.serialutil import SerialException

# Package imports
from verasleeve import actors

# Device parameters
# These are analog pins, and must be specified without an 'A' prefix as in 'A0'.
FLUID_SENSOR_PIN = 0
SURFACE_SENSOR_PINS = [1, 2, 3, 4]

class Leg(object):
    """Models the Arduino controller of the leg model test fixture."""
    def __init__(self):
        super().__init__()
        try:
            connection = nanpy.SerialManager()
            self._board = nanpy.ArduinoApi(connection=connection)
        except SerialException:
            raise RuntimeError("Could not connect to the Arduino!") from None

    def get_fluid_pressure_sensor(self):
        return self._board.analogRead(FLUID_SENSOR_PIN)

    def get_surface_pressure_sensor(self, sensor_id=0):
        return self._board.analogRead(SURFACE_SENSOR_PINS[sensor_id])

class LegMonitor(actors.Broadcaster, actors.Producer):
    """An actor to interface between a Leg instance and other actors.
    Periodically emits messages of the leg model's sensor readings.

    Public Messages:
        Data (broadcasted):
            Data messages have a time entry holding the time since the producer started
            emitting messages at which the data sample was recorded. Each data message is
            broadcast on the broadcast class corresponding to the type of data message,
            e.g. 'fluid pressure'.
            The data entry specifies the type of data message, which is the key of the entry
            holding the value of the data sample.
            fluid pressure: the reading from the fluid pressure sensor.
    """
    def __init__(self):
        super().__init__()
        self.__leg = Leg()
        self.__produce_start_time = None

    def _on_start_producing(self):
        self.__produce_start_time = time.time()
    def _on_stop_producing(self):
        self.__produce_start_time = None
    def _on_produce(self):
        self.broadcast({'data': 'fluid pressure',
                        'time': self.__time_since_produce_start(),
                        'fluid pressure': self.__leg.get_fluid_pressure_sensor()},
                       'fluid pressure')
        for surface_id in range(4):
            self.broadcast({'data': 'surface pressure',
                            'time': self.__time_since_produce_start(),
                            'surface pressure': self.__leg.get_surface_pressure_sensor(surface_id)},
                           'surface pressure {}'.format(surface_id))

    def __time_since_produce_start(self):
        return time.time() - self.__produce_start_time
