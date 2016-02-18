#!/usr/bin/env python3
"""Tests the fluid sensor."""
# Python imports
import logging
import time

# Dependency imports
import pykka

# Package imports
from .. import sleeve

logging.basicConfig(level=logging.INFO)

def control_band():
    """Continuously drives the sleeve."""
    logger = logging.getLogger(__name__)

    try:
        sleeve_controller = sleeve.IndependentSleeveController.start()
    except RuntimeError:
        pykka.ActorRegistry.stop_all() # stop actors in LIFO order
        raise
    logger.info("Controlling sleeve...")
    sleeve_controller.tell({'command': 'start producing', 'interval': 0.1})
    time.sleep(30)
    logger.info("Quitting...")
    pykka.ActorRegistry.stop_all()

if __name__ == "__main__":
    control_band()
