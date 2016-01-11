"""Defines some generic classes for pykka actors."""
# Python imports
import time
import logging

# Dependency imports
import pykka

class NamedActor(object):
    """Actor with a name for printing."""
    def __init__(self, name):
        super().__init__()
        self.__name = name

    def __str__(self):
        return "{} ({})".format(self.__class__.__name__, self.__name)

class Broadcaster(object):
    """Selectively broadcasts messages to registered actors."""
    def __init__(self):
        super().__init__()
        self.__registry = {}
        self.__logger = logging.getLogger(__name__)

    def register(self, target_actor, broadcast_class='all'):
        """Registers a target actor to listen for all messages of the specified broadcast class.

        Arguments:
            broadcast_class: the class of the message to register the target. Must be of an
            immutable data type.
            target_actor: an actor.
        """
        if broadcast_class not in self.__registry:
            self.__registry[broadcast_class] = set()
        self.__registry[broadcast_class].add(target_actor)
        self.__logger.debug("%s: registering in %s: %s", self, broadcast_class, target_actor)
    def deregister(self, target_actor, broadcast_class='all'):
        """Deregisters a previously-registered target actor from the specified broadcast class.

        Exceptions:
            ValueError: no actor is currently registered to listen for messages of the specified
            broadcast class.
        """
        try:
            self.__registry[broadcast_class].remove(target_actor)
            self.__logger.debug("%s: deregistering from %s: %s", self, broadcast_class,
                                target_actor)
        except (KeyError, ValueError):
            raise ValueError("No actor is currently registered to listen for messages of "
                             "broadcast class \"{}\"".format(broadcast_class))

    def broadcast(self, message, broadcast_class='all'):
        """Broadcasts a message to all actors registered to for the specified broadcast class."""
        self.__logger.debug("%s: broadcasting to %s: %s", self, broadcast_class, message)
        for actor in self.__registry[broadcast_class]:
            actor.tell(message)

class Producer(pykka.ThreadingActor):
    """Continuously outputs a stream of data samples at regular intervals.

    Public Messages:
        Commands:
            start producing: activates the instance to start producing data samples. Only has an
            effect if the instance is not currently producing data samples.
                interval: optional attribute. If provided, sets the interval between calls to
                _on_produce.
            stop producing: deactivates the instance to stop producing data samples. Only has an
            effect if the instance is currently producing data samples.

    Abstract methods:
        _on_produce: a method that should be implemented to generate and emit a data sample.
        Called if (and only if) the instance is producing.
        _on_start_producing: hook for setup to be done when the instance starts producing.
        _on_stop_producing: hook for cleanup to be done when the instance stops producing.
    """
    def __init__(self, interval=1):
        super().__init__()
        self.interval = interval
        self.producing = False
        self.__logger = logging.getLogger(__name__)

    def on_receive(self, message):
        self.__logger.debug("Producer %s: received %s", self, message)
        if not self.producing and message.get('command') == 'start producing':
            self.producing = True
            if 'interval' in message:
                self.__logger.debug("Producer %s: setting interval to %s", self,
                                    message['interval'])
                self.interval = message['interval']
            self._on_start_producing()
            self._produce()
        elif message.get('command') == 'stop producing':
            self.producing = False
            self._on_stop_producing()
        elif message.get('command') == 'produce':
            self._produce()
    def _produce(self):
        if not self.producing:
            return
        time.sleep(self.interval)
        self._on_produce()
        self.actor_ref.tell({'command': 'produce'})

    def _on_produce(self):
        pass
    def _on_start_producing(self):
        pass
    def _on_stop_producing(self):
        pass

class Printer(NamedActor, pykka.ThreadingActor):
    """Logs all messages it receives at the INFO level."""
    def __init__(self, name):
        super().__init__(name)
        self.__logger = logging.getLogger(__name__)

    def on_receive(self, message):
        self.__logger.info("%s: received %s", self, message)

