"""Support for signal processing."""
# Python imports
from collections import deque

# Dependency imports
import numpy as np
import pykka

# Package imports
from verasleeve import actors, coroutines

def get_interpolator(x_y, left_limit, right_limit):
    """Returns an interpolating function given a tuple of 2-tuples of x and y values."""
    (x_series, y_series) = zip(*x_y)
    return lambda interpolated_x: np.interp([interpolated_x], x_series, y_series,
                                            left_limit, right_limit)[0]

@coroutines.initialized_coroutine
def moving_filter(max_samples=None, filterer=np.median, mode="centered"):
    """A coroutine to filter a signal using its max_samples most recent samples.
    To initialize, assign to a variable and start using it - no need to call the next
    function on it or send in an initial None value.

    Arguments:
        max_samples: the window size over which to compute the filtered sample.
        To make the filter exactly symmetric in centered mode, set this to be an odd number. If this
        is None, the moving filter processes all samples and is effectively in right mode.
        mode: either "centered" or "right". If centered, the output sample number will correspond
        to the sample number for the (max_samples / 2)th most recent sample. If right, the output
        sample number will correspond to the sample number for the most recent sample.

    Sending:
        Send a two-tuple of the sample number (or sample time) and value into moving_filter to add
        that sample to the signal for filtering.
        Send a positive integer into moving_filter to reset the signal and set the filter to use
        that integer as the new value of max_samples
        Send None into moving_filter to reset the signal.

    Yielding:
        None: if the filter has not yet collected max_samples samples.
        Otherwise, a two-tuple of the sample number (or sample time) for the filtered sample and
        the filtered result (as computed by filterer) of the max_samples most recent samples.
        The sample number will be calculated depending on the mode argument.
    """
    signal_buffer = deque(maxlen=max_samples)
    sample_numbers = deque(maxlen=(max_samples // 2 + 1
                                   if max_samples is not None else None))
    filtered = None
    while True:
        value = yield filtered
        if isinstance(value, int):
            max_samples = value
            value = None
        if value is None: # reset the signal
            signal_buffer = deque(maxlen=max_samples)
            sample_numbers = deque(maxlen=(max_samples // 2 + 1
                                           if max_samples is not None else None))
            filtered = None
        else:
            sample_numbers.append(value[0])
            signal_buffer.append(value[1])
            num_samples = len(signal_buffer)
            if max_samples is None or mode == "right":
                filtered = (sample_numbers[-1], filterer(signal_buffer))
            elif num_samples == max_samples and mode == "centered":
                filtered = (sample_numbers[0], filterer(signal_buffer))
            else:
                filtered = None

class Filterer(actors.Broadcaster, pykka.ThreadingActor):
    """Filters samples of a signal.

    Public Messages:
        Data (received):
            Data messages should have a time entry holding the time of the data sample,
            corresponding to the x axis value.
            The data entry should specify the value of the data sample, corresponding to the
            y axis value.
        Command (received):
            clear: clears the filterer.
        Data (broadcasted):
            Data messages have a time entry holding the time of the data sample.
            The type entry specifies the type of the data sample, and the data is broadcasted on
            the channel named by that type.
            The data entry specifies the value of the data sample.
            The data sample will be a filtered value.
    """
    def __init__(self, filter_width=None, filterer=np.median, mode="centered"):
        super().__init__()
        self.filterer = moving_filter(filter_width, filterer, mode)

    def on_receive(self, message):
        if 'command' in message:
            self.__on_command(message)
        else:
            self.__on_data(message)

    def __on_command(self, message):
        """Processes command messages."""
        if message['command'] == 'clear':
            self.__clear_filterer()

    def __on_data(self, message):
        """Processes data messages."""
        filtered = self.filterer.send((message['time'], message['data']))
        if filtered is not None:
            new_message = dict(message)
            new_message['time'] = filtered[0]
            new_message['data'] = filtered[1]
            self.broadcast(new_message, message['type'])

    def __clear_filterer(self):
        """Clears the curve."""
        self.filterer.send(None)

class TupleSelector(actors.Broadcaster, pykka.ThreadingActor):
    """Filters a signal data from tuple-form to a single value, discarding other values.

    Public Messages:
        Data (received):
            The type entry specifies the type of data message
            The data entry should specify a tuple of values of the data sample, corresponding to
            the y axis values.
        Data (broadcasted):
            The type entry specifies the type of the data sample, and the data is broadcasted on
            the channel named by that type. If the TupleSelector's broadcast_channel property
            is set to be not-None, the type entry is changed to be broadcast_channel and the data
            is broadcasted over the broadcast_channel channel.
            The data sample will be a single value of the tuple, chosen by position from the
            actor's constructor argument.
    """
    def __init__(self, tuple_position=0, broadcast_channel=None):
        super().__init__()
        self.tuple_position = tuple_position
        self.broadcast_channel = broadcast_channel

    def on_receive(self, message):
        new_message = dict(message)
        new_message['data'] = message['data'][self.tuple_position]
        if self.broadcast_channel is not None:
            new_message['type'] = self.broadcast_channel
        self.broadcast(new_message, new_message['type'])

