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
LOW_FLUID_SENSOR_PIN = 0
HIGH_FLUID_SENSOR_PIN = 1

# Default unit conversion functions for sensors
LOW_FLUID_PRESSURE_RAW_TO_MMHG = lambda raw: (raw - 516.596) / 20.798
HIGH_FLUID_PRESSURE_RAW_TO_MMHG = lambda raw: (raw - 101.185) / 1.313
LOW_HIGH_FLUID_PRESSURE_TRANSITION_RAW = 900 # raw value where the low fluid sensor is at its limit

class Leg(object):
    """Models the Arduino controller of the leg model test fixture."""
    def __init__(self):
        super().__init__()
        try:
            connection = nanpy.SerialManager()
            self._board = nanpy.ArduinoApi(connection=connection)
        except SerialException:
            raise RuntimeError("Could not connect to the Arduino!") from None

    def get_low_fluid_pressure_sensor(self):
        """Read from the sensitive (low-range) fluid pressure sensor."""
        return self._board.analogRead(LOW_FLUID_SENSOR_PIN)
    def get_high_fluid_pressure_sensor(self):
        """Read from the high-range fluid pressure sensor."""
        return self._board.analogRead(HIGH_FLUID_SENSOR_PIN)


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
                        'data': (self.__leg.get_low_fluid_pressure_sensor(),
                                 self.__leg.get_high_fluid_pressure_sensor())},
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
            fluid pressure: 2-tuple of the raw readings from the low and high fluid pressure
            sensors, respectively.
        Data (broadcasted):
            Data messages have a time entry holding the time since the producer started
            emitting messages at which the data sample was recorded. Each data message is
            broadcast on the broadcast class corresponding to the type of data message,
            e.g. 'fluid pressure'.
            The type entry specifies the type of data message, while the data entry holds
            the value of the data sample.
            fluid pressure: the fluid pressure of the leg, in mmHg.
    """
    def __init__(self, low_raw_to_fluid_pressure=LOW_FLUID_PRESSURE_RAW_TO_MMHG,
                 high_raw_to_fluid_pressure=HIGH_FLUID_PRESSURE_RAW_TO_MMHG):
        super().__init__()
        self.__low_raw_to_fluid_pressure = low_raw_to_fluid_pressure
        self.__high_raw_to_fluid_pressure = high_raw_to_fluid_pressure

    def on_receive(self, message):
        self.__on_data(message)

    def __on_data(self, message):
        """Processes data messages."""
        new_message = dict(message)
        if message['type'] == 'fluid pressure':
            new_message['data'] = self.__raw_to_fluid_pressure(*(message['data']))
        self.broadcast(new_message, new_message['type'])
    def __raw_to_fluid_pressure(self, low_raw, high_raw):
        if low_raw <= LOW_HIGH_FLUID_PRESSURE_TRANSITION_RAW:
            return self.__low_raw_to_fluid_pressure(low_raw)
        else:
            return self.__high_raw_to_fluid_pressure(high_raw)

