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
    def __init__(self, label, label_name_override=None):
        super().__init__()
        self.label = label
        self.label_name = label_name_override

    def on_receive(self, message):
        """Slot that updates the text label with the next sample."""
        label_name = message['type'] if self.label_name is None else self.label_name
        self.label.setText("{}: {:.1f}".format(label_name, message['data']))

