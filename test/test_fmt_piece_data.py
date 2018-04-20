import unittest
import mud
import mud.fmt.feature as feature
import mud.fmt.label as label
import numpy as np

class TestEventData(unittest.TestCase):
    def test(self):
        event = mud.Event(mud.Note('A6', 1.0), 2.0)
        event = mud.SlicedEvent((2.0, 2.5), event)
        # The event is a 1/2 note slice that continues into the next slice.
        formatter = mud.fmt.EventDataBuilder(
            features=(feature.IsNote(),
                      feature.IsRest(),
                      feature.NoteRelativePitch(),
                      feature.ContinuesNextEvent()),
            labels  =(label.RelativePitchLabels(),
                      label.ContinuesNextEventLabel())
        )
        event_data = mud.fmt.EventData(event, formatter)
        self.assertEqual(event_data.vec.tolist(), [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
        self.assertEqual(event_data.labels, (9, 1))
