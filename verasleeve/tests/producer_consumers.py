#!/usr/bin/env python3
"""Tests actor-based concurrency with pykka."""
# Python imports
import random
import time
import logging

# Dependency imports
import pykka

# Package imports
from .. import actors

logging.basicConfig(level=logging.INFO)

class NumberGenerator(actors.NamedActor, actors.Broadcaster, actors.Producer):
    """Generates random integers."""
    def __init__(self, name):
        super().__init__(name)

    def _on_produce(self):
        number = random.randint(0, 9)
        if number % 2 == 0:
            self.broadcast({'number': number}, 'even number')
        else:
            self.broadcast({'number': number}, 'odd number')

def produce_consume():
    """Prints data to the console using a producer and consumers."""
    logger = logging.getLogger(__name__)

    even_consumer = actors.Printer.start("Even Printer")
    odd_consumer = actors.Printer.start("Odd Printer")
    producer = NumberGenerator.start("RNG")
    producer.proxy().register(even_consumer, 'even number')
    producer.proxy().register(odd_consumer, 'odd number')

    logger.info("Producing for 2 seconds at an interval of 0.1 seconds...")
    producer.tell({'command': 'start producing', 'interval': 0.1})
    time.sleep(2)
    producer.tell({'command': 'stop producing'})
    time.sleep(2)
    logger.info("Producing for 2 seconds at an interval of 0.5 seconds...")
    producer.tell({'command': 'start producing', 'interval': 0.5})
    time.sleep(2)
    producer.tell({'command': 'stop producing'})
    time.sleep(2)
    logger.info("Producing for 2 seconds...")
    producer.tell({'command': 'start producing'})
    time.sleep(2)
    producer.tell({'command': 'stop producing'})
    logger.info("Quitting")

    pykka.ActorRegistry.stop_all() # stop actors in LIFO order

if __name__ == "__main__":
    produce_consume()
