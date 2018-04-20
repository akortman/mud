import unittest
import mud
import mud.fmt.feature as feature
import mud.fmt.label as label
import numpy as np

formatter = mud.fmt.EventDataBuilder(
    features=(feature.IsNote(),
                feature.IsRest(),
                feature.NoteRelativePitch(),
                feature.ContinuesNextEvent()),
    labels  =(label.RelativePitchLabels(),
                label.ContinuesNextEventLabel())
)

class TestEventData(unittest.TestCase):
    def test(self):
        event = mud.Event(mud.Note('A6', 1.0), 2.0)
        event = mud.SlicedEvent((2.0, 2.5), event)
        # The event is a 1/2 note slice that continues into the next slice.
        event_data = mud.fmt.EventData(event, formatter)
        self.assertEqual(event_data.vec.tolist(),
                         [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
        self.assertEqual(event_data.labels, (9, 1))

class TestTimeSliceData(unittest.TestCase):
    def test(self):
        span = mud.Span([
            (mud.Note('C4', 1), mud.Time(0)),
            (mud.Note('G5', 1), mud.Time(0)),
            (mud.Rest(      1), mud.Time(1)),
            (mud.Note('C4', 2), mud.Time(2)),
            (mud.Note('A4', 2), mud.Time(2)),
        ])
        ts = mud.TimeSlice(span, (2.0, 3.0))
        ts_data = mud.fmt.TimeSliceData(ts, formatter)
        
        self.assertEqual(len(ts_data.events), 2)
        self.assertTrue([isinstance(event_data, mud.fmt.EventData)
                            for event_data in ts_data.events],
                        [True for _ in ts_data.events])
                        
        self.assertEqual(ts_data.events[0].vec.tolist(),
                         [1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
        self.assertEqual(ts_data.events[0].labels, (0, 1))

        self.assertEqual(ts_data.events[1].vec.tolist(),
                         [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
        self.assertEqual(ts_data.events[1].labels, (9, 1))

class TestBarData(unittest.TestCase):
    pass

class TestPieceData(unittest.TestCase):
    pass