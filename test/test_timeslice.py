import unittest
import mud

class TestTimeSlice(unittest.TestCase):
    def test_raw_events(self):
        events = [
            mud.Event(mud.Note('C4', 1), mud.Time(0)),
            mud.Event(mud.Note('G5', 1), mud.Time(0)),
            mud.Event(mud.Rest(      1), mud.Time(1)),
            mud.Event(mud.Note('C4', 2), mud.Time(2)),
            mud.Event(mud.Note('A4', 2), mud.Time(2)),
        ]
        span = mud.Span(events, length=4, offset=4)
        
        # Test slices which intersect with the first two notes
        slices_first_two = [
            mud.TimeSlice(span, (0.0, 0.4)),
            mud.TimeSlice(span, (0.6, 1.0)),
            mud.TimeSlice(span, (0.3, 0.7)),
            mud.TimeSlice(span, (0.0, 1.0)),
        ]
        for ts in slices_first_two:
            self.assertEqual(ts.num_events(), 2)
            for i, event in enumerate(ts.raw_events()):
                self.assertEqual(event, events[i])
                self.assertLess(i, 2)

        # Test slicing the rest.
        slices_rest = [
            mud.TimeSlice(span, (1.0, 2.0)),
            mud.TimeSlice(span, (1.1, 1.2)),
        ]
        for ts in slices_rest:
            self.assertEqual(ts.num_events(), 1)
            for i, event in enumerate(ts.raw_events()):
                self.assertEqual(event, events[2])
                self.assertLess(i, 1)

    def test_sliced_events(self):
        events = [
            mud.Event(mud.Note('C4', 1), mud.Time(0)),
            mud.Event(mud.Note('G5', 1), mud.Time(0)),
            mud.Event(mud.Rest(      1), mud.Time(1)),
            mud.Event(mud.Note('C4', 2), mud.Time(2)),
            mud.Event(mud.Note('A4', 2), mud.Time(2)),
        ]
        span = mud.Span(events, length=4, offset=4)

        ts = mud.TimeSlice(span, (2.5, 3.0))
        self.assertEqual(ts.num_events(), 2)

        sliced_events = list(ts.sliced_events())
        self.assertEqual(len(sliced_events), 2)

        self.assertNotEqual(sliced_events[0],
                            mud.Event(mud.Note('C4', 2.0), mud.Time(2)))
        self.assertNotEqual(sliced_events[0],
                            mud.Event(mud.Note('C4', 0.5), mud.Time(2)))
        self.assertEqual(sliced_events[0].time(), mud.Time(2.5))
        self.assertEqual(sliced_events[0].duration(), mud.Duration(0.5))
        se0 = mud.SlicedEvent((2.5, 3.0), mud.Event(mud.Note('C4', 2), mud.Time(2)))
        self.assertEqual(sliced_events[0], se0)

        self.assertEqual(sliced_events[1].time(), mud.Time(2.5))
        self.assertEqual(sliced_events[1].duration(), mud.Duration(0.5))
        se1 = mud.SlicedEvent((2.5, 3.0), mud.Event(mud.Note('A4', 2), mud.Time(2)))
        self.assertEqual(sliced_events[1], se1)
