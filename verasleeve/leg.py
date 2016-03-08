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
TOP_LOW_FLUID_SENSOR_PIN = 0
TOP_HIGH_FLUID_SENSOR_PIN = 1
BOTTOM_FLUID_SENSOR_PIN = 2

# Default unit conversion functions for sensors
TOP_LOW_FLUID_PRESSURE_RAW_TO_MMHG = lambda raw: (raw - 499.435) / 8.266
TOP_HIGH_FLUID_PRESSURE_RAW_TO_MMHG = lambda raw: (raw - 111.514) / 2.723
TOP_LOW_HIGH_FLUID_PRESSURE_TRANSITION_RAW = 900 # raw value where the low fluid sensor is at limit
BOTTOM_FLUID_PRESSURE_RAW_TO_MMHG = lambda raw: (raw - 105.287) / 2.729

class Leg(object):
    """Models the Arduino controller of the leg model test fixture."""
    def __init__(self, connection=None):
        super().__init__()
        if connection is None:
            try:
                connection = nanpy.SerialManager()
            except SerialException:
                raise RuntimeError("Could not connect to the Arduino!") from None
        self._board = nanpy.ArduinoApi(connection=connection)

    def get_top_low_fluid_pressure_sensor(self):
        """Read from the sensitive (low-range) fluid pressure sensor above the vein."""
        return self._board.analogRead(TOP_LOW_FLUID_SENSOR_PIN)
    def get_top_high_fluid_pressure_sensor(self):
        """Read from the high-range fluid pressure sensor top the vein."""
        return self._board.analogRead(TOP_HIGH_FLUID_SENSOR_PIN)
    def get_bottom_fluid_pressure_sensor(self):
        """Read from the high-range fluid pressure sensor below the vein."""
        return self._board.analogRead(BOTTOM_FLUID_SENSOR_PIN)

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
            fluid pressure: 2-tuple of the raw readings from the low and high fluid pressure
            sensors, respectively.
    """
    def __init__(self, leg=None):
        super().__init__()
        if leg is None:
            leg = Leg()
        self.__leg = leg
        self.__produce_start_time = None

    def _on_start_producing(self):
        self.__produce_start_time = time.time()
    def _on_stop_producing(self):
        self.__produce_start_time = None
    def _on_produce(self):
        self.broadcast({'type': 'fluid pressure',
                        'time': self.__time_since_produce_start(),
                        'data': (self.__leg.get_top_low_fluid_pressure_sensor(),
                                 self.__leg.get_top_high_fluid_pressure_sensor(),
                                 self.__leg.get_bottom_fluid_pressure_sensor())},
                       'fluid pressure')

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
            fluid pressure: 3-tuple of the raw readings from the low and high fluid pressure
            sensors at the top of the vein and the fluid pressure sensor at the bottom of the vein,
            respectively.
        Data (broadcasted):
            Data messages have a time entry holding the time since the producer started
            emitting messages at which the data sample was recorded. Each data message is
            broadcast on the broadcast class corresponding to the type of data message,
            e.g. 'fluid pressure'.
            The type entry specifies the type of data message, while the data entry holds
            the value of the data sample.
            fluid pressure: a 2-tuple of the fluid pressures at the top and bottom of the vein,
            respectively, in mmHg.
    """
    def __init__(self, top_low_raw_to_fluid_pressure=TOP_LOW_FLUID_PRESSURE_RAW_TO_MMHG,
                 top_high_raw_to_fluid_pressure=TOP_HIGH_FLUID_PRESSURE_RAW_TO_MMHG,
                 bottom_raw_to_fluid_pressure=BOTTOM_FLUID_PRESSURE_RAW_TO_MMHG):
        super().__init__()
        self.__top_low_raw_to_fluid_pressure = top_low_raw_to_fluid_pressure
        self.__top_high_raw_to_fluid_pressure = top_high_raw_to_fluid_pressure
        self.__bottom_raw_to_fluid_pressure = bottom_raw_to_fluid_pressure

    def on_receive(self, message):
        self.__on_data(message)

    def __on_data(self, message):
        """Processes data messages."""
        new_message = dict(message)
        if message['type'] == 'fluid pressure':
            new_message['data'] = (self.__top_raw_to_fluid_pressure(message['data'][0],
                                                                    message['data'][1]),
                                   self.__bottom_raw_to_fluid_pressure(message['data'][2]))
        self.broadcast(new_message, new_message['type'])
    def __top_raw_to_fluid_pressure(self, top_low_raw, top_high_raw):
        if top_low_raw <= TOP_LOW_HIGH_FLUID_PRESSURE_TRANSITION_RAW:
            return self.__top_low_raw_to_fluid_pressure(top_low_raw)
        else:
            return self.__top_high_raw_to_fluid_pressure(top_high_raw)

