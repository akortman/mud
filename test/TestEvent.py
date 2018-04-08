import unittest
import mud

class TestSpan(unittest.TestCase):
    def test_creation(self):
        n = mud.Note('G#6', 2)
        t = mud.Time(2)

        event = mud.Event(n, t)
        self.assertEqual(event.unwrap(), n)
        self.assertEqual(event.unwrap(), mud.Note('G#6', mud.Duration(2.0)))
        self.assertEqual(event.time(), t)
        self.assertEqual(event.time(), mud.Time(2.0, resolution=0.5))

        (n2, t2) = event
        self.assertEqual(n, n2)
        self.assertEqual(t, t2)

    def test_copy(self):
        n = mud.Note('D5', 0.5)
        t = mud.Time(2)
        event = mud.Event(n, t)
        event2 = mud.Event(event)

        self.assertEqual(event, event2)
        self.assertEqual(event2.unwrap(), n)
        self.assertEqual(event2.time(), t)

    def test_in_span_range(self):
        # Event is from 2.5 to 0.5
        n = mud.Note('D5', 0.5)
        t = mud.Time(2)
        event = mud.Event(n, t)
        # Exact
        self.assertTrue(event.in_span_range((2.0, 2.5)))
        # End before start
        with self.assertRaises(ValueError):
            event.in_span_range((2.5, 2.3))
        # Span starts before
        self.assertTrue(event.in_span_range((1.5, 2.5)))
        # Span ends after
        self.assertTrue(event.in_span_range((2.0, 4.0)))
        # Span starts before and ends after
        self.assertTrue(event.in_span_range((0.0, 3.0)))
        # Span starts inside and ends inside
        self.assertTrue(event.in_span_range((2.3, 2.4)))
        # Span starts inside and ends after
        self.assertTrue(event.in_span_range((2.3, 3.1)))
        # Span starts before and ends inside
        self.assertTrue(event.in_span_range((1.8, 2.4)))

        # Span starts before and ends before
        self.assertFalse(event.in_span_range((1.8, 1.9)))
        # Span starts after and ends after
        self.assertFalse(event.in_span_range((2.6, 5.0)))
