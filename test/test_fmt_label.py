import unittest
import mud
import mud.fmt.label as label

class TestPitchLabels(unittest.TestCase):
    def test(self):
        pass

class TestRelativePitchLabels(unittest.TestCase):
    def test(self):
        pass

class TestContinuingPreviousEventLabel(unittest.TestCase):
    def test(self):
        l = label.ContinuingPreviousEventLabel()
        event = mud.Event(mud.Note('A6', mud.Time(4.0)), mud.Time(0.0))
        self.assertEqual(l.get_event_label(event), 0)

        # middle slice
        sliced_event = mud.SlicedEvent((2.0, 3.0), event)
        self.assertFalse(sliced_event.is_note_start())
        self.assertEqual(l.get_event_label(sliced_event), 1)

        # no slice
        sliced_event = mud.SlicedEvent((0.0, 4.0), event)
        self.assertTrue(sliced_event.is_note_start())
        self.assertEqual(l.get_event_label(sliced_event), 0)

        # slice from start
        sliced_event = mud.SlicedEvent((2.0, 4.0), event)
        self.assertFalse(sliced_event.is_note_start())
        self.assertEqual(l.get_event_label(sliced_event), 1)

class TestContinuesNextEventLabel(unittest.TestCase):
    def test(self):
        l = label.ContinuesNextEventLabel()
        event = mud.Event(mud.Note('A6', mud.Time(4.0)), mud.Time(0.0))
        self.assertEqual(l.get_event_label(event), 0)

        # middle slice
        sliced_event = mud.SlicedEvent((2.0, 3.0), event)
        self.assertFalse(sliced_event.is_note_end())
        self.assertEqual(l.get_event_label(sliced_event), 1)

        # no slice
        sliced_event = mud.SlicedEvent((0.0, 4.0), event)
        self.assertTrue(sliced_event.is_note_end())
        self.assertEqual(l.get_event_label(sliced_event), 0)

        # slice from start
        sliced_event = mud.SlicedEvent((0.0, 3.5), event)
        self.assertFalse(sliced_event.is_note_end())
        self.assertEqual(l.get_event_label(sliced_event), 1)

class TestSpanPosition(unittest.TestCase):
    def test(self):
        l = label.SpanPosition(resolution=0.25, span_length=4.0)
        self.assertEqual(l.num_labels, 16)
        event = mud.Event(mud.Note('E3', 1.0), 2.0)
        self.assertEqual(l.get_event_label(event), 8)

class TestNoteLength(unittest.TestCase):
    def test(self):
        l = label.NoteLength(resolution=0.5, max_length=4.0)
        self.assertEqual(l.num_labels, 8)
        event = mud.Event(mud.Note('E3', 1.0), 2.0)
        self.assertEqual(l.get_event_label(event), 2)

class TestBooleanFlag(unittest.TestCase):
    def test(self):
        l = label.BooleanFlag('flag')
        event = mud.Event(mud.Note('A6', mud.Time(4.0)), mud.Time(0.0))
        self.assertEqual(l.get_event_label(event), 0)
        self.assertEqual(l.get_event_label(event, flag=False), 0)
        self.assertEqual(l.get_event_label(event, flag=True), 1)
