#!/usr/bin/env python3
"""Tests signal filtering."""
# Python imports
import sys
import time
import random
from collections import deque

# Dependency imports
import numpy as np
import pyqtgraph as pg

# Package imports
from .. import signal

def square_wave(length, gaussian_noisiness=2, salt_pepper_noisiness=2, amplitude=100):
    """Returns a noisy square wave signal.
    High values have gaussian noise, while low values have salt-and-pepper noise.
    """
    i = 0
    while i < length:
        for _ in range(0, 50):
            yield (i, 0 + random.gauss(0, gaussian_noisiness))
            i = i + 1
        for _ in range(0, 50):
            yield (i, amplitude * (random.randint(0, amplitude - 1) > salt_pepper_noisiness))
            i = i + 1
def sine_wave(length, gaussian_noisiness=2, amplitude=50):
    """Returns a noisy sine wave signal with gaussian noise."""
    i = 0
    sample_points = np.linspace(0.0, 2 * np.pi, num=length)
    wave = amplitude * (1 + np.sin(2 * np.pi * sample_points))
    for i in range(0, length):
        yield (i, wave[i] + random.gauss(0, gaussian_noisiness))

def stream(signal_generator):
    """Continuously generates noisy data and filters it."""
    signal_length = 500
    filterer = signal.moving_filter(10)

    # Plotting
    signal_x = []
    signal_y = []
    filtered_x = []
    filtered_y = []

    for (sample_number, sample) in signal_generator(signal_length):
        signal_x.append(sample_number)
        signal_y.append(sample)
        filtered = filterer.send((sample_number, sample))
        if filtered is not None:
            filtered_x.append(filtered[0])
            filtered_y.append(filtered[1])

    graph = pg.plot()
    graph.addLegend()
    raw_curve = graph.plot(signal_x, signal_y, pen='r', name="Raw (Noisy) Signal")
    filtered_curve = graph.plot(filtered_x, filtered_y, pen='b', name="Filtered Signal")
    #ax1.plot(signal_x, signal_y)
    #ax1.set_title('Signal')
    #ax1.set_ylim([-10, 110])
    #ax2.plot(filtered_x, filtered_y)
    #ax2.set_title('Filtered')
    #plt.show()


if __name__ == "__main__":
    pg.setConfigOptions(antialias=True, background='w', foreground='k')
    stream(square_wave)
    stream(sine_wave)
    pg.Qt.QtGui.QApplication.instance().exec_()
