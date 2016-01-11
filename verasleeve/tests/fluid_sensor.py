#!/usr/bin/env python3
"""Tests the fluid sensor."""
# Python imports
import logging
# Package imports
from .. import actors, leg

logging.basicConfig(level=logging.INFO)

def stream():
    """Continuously prints the pin value on the fluid pressure sensor."""
    printer = actors.Printer.start('Printer')
    leg_monitor = leg.LegMonitor().start()
    leg_monitor.proxy().register(printer, 'fluid pressure')
    leg_monitor.tell({'command': 'start producing', 'interval': 0.01})

if __name__ == "__main__":
    stream()
