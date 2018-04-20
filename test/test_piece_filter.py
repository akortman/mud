import unittest
import mud

class TestAtomicSlicable(unittest.TestCase):
    def test(self):
        p = mud.Piece()
        p.build_from_spans(mud.Span([
            (mud.Note('C4', 1), mud.Time(0)),
            (mud.Note('G5', 1), mud.Time(0)),
            (mud.Rest(      1), mud.Time(1)),
            (mud.Note('C4', 2), mud.Time(2)),
            (mud.Note('A4', 2), mud.Time(2)),
        ]))
        self.assertTrue(mud.piece_filter.AtomicSlicable(0.25)(p))
        self.assertTrue(mud.piece_filter.AtomicSlicable(1.0)(p))
        self.assertFalse(mud.piece_filter.AtomicSlicable(1.5)(p))

@unittest.skip('Not implemented')
class NotesWithinRange(unittest.TestCase):
    def test(self):
        pass

@unittest.skip('Not implemented')
class TimeSignature(unittest.TestCase):
    def test(self):
        pass