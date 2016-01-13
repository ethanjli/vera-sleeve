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
            The data entry should specify the key of the entry holding the value of the data
            sample, corresponding to the y axis value.
    """
    def __init__(self, curve, max_samples=None):
        super().__init__()
        self.curve = curve
        self.curve_x = deque(maxlen=max_samples)
        self.curve_y = deque(maxlen=max_samples)

    def on_receive(self, message):
        """Slot that updates the curves with the next sample."""
        sample_time = message['time']
        sample = message[message['data']]
        self.curve_x.append(sample_time)
        self.curve_y.append(sample)
        self.curve.setData(self.curve_x, self.curve_y)

