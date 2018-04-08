import unittest
import mud

class TestSpan(unittest.TestCase):
    def test(self):
        events = [
            (mud.Note('C4', 1), mud.Time(0)),
            (mud.Note('G5', 1), mud.Time(0)),
            (mud.Rest(      1), mud.Time(1)),
            (mud.Note('C4', 2), mud.Time(2)),
            (mud.Note('A4', 2), mud.Time(2)),
        ]
        span = mud.Span(events, length=4, offset=4)
        self.assertAlmostEqual(span.length(), 4.0)
        self.assertAlmostEqual(span.offset(), 4.0)

        for i, (event, time) in enumerate(events):
            self.assertEqual(span[i], mud.Event(event, time))