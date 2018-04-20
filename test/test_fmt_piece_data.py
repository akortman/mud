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
    def test(self):
        span = mud.Span([
            (mud.Note('C4', 1), mud.Time(0)),
            (mud.Note('G5', 1), mud.Time(0)),
            (mud.Rest(      1), mud.Time(1)),
            (mud.Note('C4', 2), mud.Time(2)),
            (mud.Note('A4', 2), mud.Time(2)),
        ])
        bar_data = mud.fmt.BarData(span, formatter, slice_resolution=0.5)

        self.assertEqual(len(bar_data.timeslices), 8)
        self.assertTrue([isinstance(ts_data, mud.fmt.TimeSliceData)
                            for ts_data in bar_data.timeslices],
                        [True for _ in bar_data.timeslices])
        
        ts_data = bar_data.timeslices[1]
        self.assertEqual(len(ts_data.events), 2)

        self.assertEqual(ts_data.events[0].vec.tolist(),
                         [1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(ts_data.events[0].labels, (0, 0))

        self.assertEqual(ts_data.events[1].vec.tolist(),
                         [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.assertEqual(ts_data.events[1].labels, (7, 0))

        # Test rest.
        ts_rest_data = bar_data.timeslices[2]
        self.assertEqual(len(ts_rest_data.events), 1)
        self.assertEqual(ts_rest_data.events[0].vec.tolist(),
                         [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
        self.assertEqual(ts_rest_data.events[0].labels, (None, 1))

class TestPieceData(unittest.TestCase):
    def test(self):
        pass