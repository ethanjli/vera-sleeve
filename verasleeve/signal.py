"""Support for signal processing."""
# Python imports
from collections import deque

# Dependency imports
import numpy as np

# Package imports
from verasleeve import coroutines

def get_interpolator(x_y, left_limit, right_limit):
    """Returns an interpolating function given a tuple of 2-tuples of x and y values."""
    (x_series, y_series) = zip(*x_y)
    return lambda interpolated_x: np.interp([interpolated_x], x_series, y_series,
                                            left_limit, right_limit)[0]

@coroutines.initialized_coroutine
def moving_filter(max_samples=None, filterer=np.median):
    """A coroutine to filter a signal using its max_samples most recent samples.
    To initialize, assign to a variable and start using it - no need to call the next
    function on it or send in an initial None value.

    Arguments:
        max_samples: the window size over which to compute the filtered sample.
        To make the filter exactly symmetric, set this to be an odd number. If this
        is None, the moving filter processes all samples.

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
        The sample number will correspond to the sample number for the (max_samples / 2)th most
        recent sample.
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
            if max_samples is None:
                filtered = (sample_numbers[-1], filterer(signal_buffer))
            elif num_samples == max_samples:
                filtered = (sample_numbers[0], filterer(signal_buffer))
            else:
                filtered = None

