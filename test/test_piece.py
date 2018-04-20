import unittest
import mud

class TestPiece(unittest.TestCase):
    def test(self):
        p = mud.Piece('./test/test-files/piece.musicxml')
        self.assertEqual(p.name, './test/test-files/piece.musicxml')
        self.assertEqual(p.count_events(), 1)
        bar = p.bars()[0]
        self.assertAlmostEqual(bar.offset().in_beats(), 0.0)
        self.assertAlmostEqual(bar.length().in_beats(), 4.0)
        self.assertEqual(bar.num_events(), 1)
        note, time = bar[0]
        self.assertEqual(time, mud.Time(0))
        pitch, duration = note
        self.assertEqual(note, mud.Note('Db4', mud.Time(4.0)))
        self.assertEqual(pitch, mud.Pitch('Db4'))
        self.assertEqual(duration, mud.Time(4))

    def test_complex_piece(self):
        # Canon in D violin solo from https://musescore.com/user/88585/scores/105013
        p = mud.Piece('./test/test-files/canon_in_d.mxl')
        self.assertEqual(p.name, './test/test-files/canon_in_d.mxl')
        self.assertEqual(p.num_bars(), 27)
        bar = p.bars()[22]
        self.assertEqual(bar.num_events(), 4)
        
        # note 0: D, quarter note
        note, time = bar[0]
        self.assertEqual(note, mud.Note('D5', 1.0))
        self.assertEqual(time, mud.Time(0.0))

        # note 3: F, quarter note
        note, time = bar[3]
        self.assertEqual(note, mud.Note('F#4', 1.0))
        self.assertEqual(time, mud.Time(3.0))

    def test_polyphonic(self):
        return
        # mii channel theme from from https://musescore.com/pimplup/mii-channel-music
        p = mud.Piece('./test/test-files/mii_channel.mxl')
        self.assertEqual(p.num_bars(), 25)
        bar = p.bars()[0]
        self.assertEqual(bar.num_events(), 15)
        self.assertAlmostEqual(bar.length(), 4.0)