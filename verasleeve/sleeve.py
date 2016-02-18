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

class SleeveController(actors.Producer):
    """An abstract actor to control the contractions of a leg sleeve."""
    def __init__(self, sleeve_servos=None):
        super().__init__()
        if sleeve_servos is None:
            sleeve_servos = SleeveServos()
        self.__sleeve_servos = sleeve_servos
        self.__produce_start_time = None

    def _on_start_producing(self):
        self.__produce_start_time = time.time()
    def _on_stop_producing(self):
        print("stop producing")
        self.__produce_start_time = None
    def _on_produce(self):
        for servo_id in BAND_SERVO_IDS:
            self.__sleeve_servos.set_servo_position(servo_id, self._get_position(servo_id))

    def on_stop(self):
        self.__sleeve_servos.quit()

    def _time_since_produce_start(self):
        return time.time() - self.__produce_start_time
    def _get_position(self, servo_id):
        """Abstract method returning a servo position for the specified servo.
        Implement this method to define sleeve contraction behavior."""
        return 0

class AdditiveSleeveController(SleeveController):
    """Contracts sleeve bands in an additive sequential square-wave manner."""
    def __init__(self, sleeve=None, period=2 * (1 + NUM_BANDS), duty=1 / (1 + NUM_BANDS),
                 delay_per_band=2, min_pos=130, max_pos=50):
        super().__init__(sleeve)
        self.period = period
        self.duty = duty
        self.delay_per_band = delay_per_band
        self.min_pos = min_pos
        self.max_pos = max_pos

    def __time_since_cycle_start(self):
        return self._time_since_produce_start() % self.period
    def _get_position(self, servo_id):
        adjusted_time = self.__time_since_cycle_start() - self.delay_per_band * servo_id
        whether_contract = (adjusted_time < self.period and adjusted_time > self.duty * self.period)
        return self.min_pos + (self.max_pos - self.min_pos) * int(whether_contract)
