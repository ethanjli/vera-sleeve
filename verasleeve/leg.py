"""Controls the Arduino board of the leg model test fixture."""
# Python imports
import time

# Dependency imports
import nanpy
from serial.serialutil import SerialException
import pykka

# Package imports
from verasleeve import actors

# Device parameters
# These are analog pins, and must be specified without an 'A' prefix as in 'A0'.
FLUID_SENSOR_PIN = 0
SURFACE_SENSOR_PINS = [1]
SURFACE_SENSOR_IDS = range(len(SURFACE_SENSOR_PINS))

# Default unit conversion functions for sensors
FLUID_PRESSURE_RAW_TO_MMHG = lambda raw: (raw - 100) / 0.535

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
            The type entry specifies the type of data message, while the data entry holds
            the value of the data sample.
            fluid pressure: the reading from the fluid pressure sensor.
            surface pressure n: the reading from the surface pressure sensor with id n.
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
        self.broadcast({'type': 'fluid pressure',
                        'time': self.__time_since_produce_start(),
                        'data': self.__leg.get_fluid_pressure_sensor()},
                       'fluid pressure')
        for sensor_id in SURFACE_SENSOR_IDS:
            self.broadcast({'type': 'surface pressure {}'.format(sensor_id),
                            'time': self.__time_since_produce_start(),
                            'data': self.__leg.get_surface_pressure_sensor(sensor_id)},
                           'surface pressure {}'.format(sensor_id))

    def __time_since_produce_start(self):
        return time.time() - self.__produce_start_time

class LegUnitConverter(actors.Broadcaster, pykka.ThreadingActor):
    """Converts raw sensor value data from a LegMonitor into physical units.
    Passes through any data messages it doesn't recognize as amenable to unit conversion.

    Public Messages:
        Data (received):
            Data messages should have a time entry holding the time since the producer started
            emitting messages at which the data sample was recorded. The type entry should specify
            the type of data message, while the data entry holds the raw sensor value of the
            data sample.
            fluid pressure: the raw reading from the fluid pressure sensor.
            surface pressure n: the raw reading from the surface pressure sensor with id n.
        Data (broadcasted):
            Data messages have a time entry holding the time since the producer started
            emitting messages at which the data sample was recorded. Each data message is
            broadcast on the broadcast class corresponding to the type of data message,
            e.g. 'fluid pressure'.
            The type entry specifies the type of data message, while the data entry holds
            the value of the data sample.
            fluid pressure: the reading from the fluid pressure sensor.
            surface pressure n: the reading from the surface pressure sensor with id n.
    """
    def __init__(self, raw_to_fluid_pressure=FLUID_PRESSURE_RAW_TO_MMHG):
        super().__init__()
        self.raw_to_fluid_pressure = raw_to_fluid_pressure

    def on_receive(self, message):
        self.__on_data(message)

    def __on_data(self, message):
        """Processes data messages."""
        new_message = dict(message)
        if message['type'] == 'fluid pressure':
            new_message['data'] = self.raw_to_fluid_pressure(message['data'])
        self.broadcast(new_message, new_message['type'])

