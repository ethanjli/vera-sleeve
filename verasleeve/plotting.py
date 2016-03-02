"""Controls the Arduino board of the leg model test fixture."""
# Python imports
from collections import deque

# Dependency imports
import pykka

class CurveUpdater(pykka.ThreadingActor):
    """Updates a PyQtGraph curve with samples.

    Public Messages:
        Data (received):
            Data messages should have a time entry holding the time of the data sample,
            corresponding to the x axis value.
            The data entry should specify the value of the data sample, corresponding to the
            y axis value.
        Command (received):
            clear: clears the curve.
            show: starts plotting the curve.
            hide: clears and hides the curve.
    """
    def __init__(self, curve, max_samples=None):
        super().__init__()
        self.curve = curve
        self.max_samples = max_samples
        self.curve_x = None
        self.curve_y = None
        self.__plotting = True
        self.__clear_curve()

    def on_receive(self, message):
        """Slot that updates the curves with the next sample."""
        if 'command' in message:
            self.__on_command(message)
        else:
            self.__on_data(message)

    def __on_command(self, message):
        """Processes command messages."""
        if message['command'] == 'clear':
            self.__clear_curve()
        elif message['command'] == 'show':
            self.__plotting = True
            self.curve.setData(self.curve_x, self.curve_y)
        elif message['command'] == 'hide':
            self.__plotting = False
            self.__clear_curve()

    def __on_data(self, message):
        """Processes data messages."""
        sample_time = message['time']
        sample = message['data']
        self.curve_x.append(sample_time)
        self.curve_y.append(sample)
        if self.__plotting:
            self.curve.setData(self.curve_x, self.curve_y)

    def __clear_curve(self):
        """Clears the curve."""
        self.curve_x = deque(maxlen=self.max_samples)
        self.curve_y = deque(maxlen=self.max_samples)
        self.curve.setData(self.curve_x, self.curve_y)

