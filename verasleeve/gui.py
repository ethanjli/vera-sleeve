"""Defines some actors for graphical interfaces."""

# Dependency imports
import pykka

class LabelUpdater(pykka.ThreadingActor):
    """Updates a Qt label with sample data.

    Public Messages:
        Data (received):
            The data entry should specify the key of the entry holding the value of the data
            sample. This key will be printed with the data value.
    """
    def __init__(self, label):
        super().__init__()
        self.label = label

    def on_receive(self, message):
        """Slot that updates the text label with the next sample."""
        self.label.setText("{}: {}".format(message['type'], message['data']))

