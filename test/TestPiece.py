import unittest
import mud

class TestPiece(unittest.TestCase):
    def test(self):
        p = mud.Piece('./test/test-files/piece.musicxml')
        self.assertEqual(p.num_bars(), 1)
        self.assertEqual(p.count_events(), 1)
        bar = p.bars()[0]
        self.assertAlmostEqual(bar.offset().in_beats(), 0.0)
        self.assertAlmostEqual(bar.length(), 4.0)
        self.assertEqual(bar.num_events(), 1)
        note, time = bar[0]
        self.assertEqual(time, mud.Duration(0))
        pitch, duration = note
        self.assertEqual(note, mud.Note('Db4', mud.Duration(4.0)))
        self.assertEqual(pitch, mud.Pitch('Db4'))
        self.assertEqual(duration, mud.Duration(4))