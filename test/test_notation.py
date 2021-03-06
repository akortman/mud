import unittest
import mud
import music21 as mu

class TestPitch(unittest.TestCase):
    def test_create_relative(self):
        p = mud.Pitch(4)
        self.assertEqual(p.relative_pitch(), 4)
        self.assertEqual(p.octave(), None)
        with self.assertRaises(ValueError):
            p.midi_pitch()
        self.assertEqual(p.name(), 'E')
        self.assertEqual(p, mud.Pitch(4, None))

    def test_create_pitch_and_octave(self):
        p = mud.Pitch(8, 5)
        self.assertEqual(p.relative_pitch(), 8)
        self.assertEqual(p.midi_pitch(), 80)
        self.assertEqual(p.octave(), 5)
        self.assertEqual(p.name(), 'Ab5')
        self.assertEqual(p, mud.Pitch(8, 5))

    def test_create_str(self):
        p = mud.Pitch('Db4')
        self.assertEqual(p.relative_pitch(), 1)
        self.assertEqual(p.octave(), 4)
        self.assertEqual(p.name(), 'Db4')
        self.assertEqual(p, mud.Pitch(1, 4))
        self.assertEqual(p, mud.Pitch('Db4'))
        self.assertEqual(p, mud.Pitch('C#4'))

    def test_create_str_and_octave(self):
        p = mud.Pitch('G#', 6)
        self.assertEqual(p.relative_pitch(), 8)
        self.assertEqual(p.octave(), 6)
        self.assertEqual(p.name(), 'Ab6')
        self.assertEqual(p, mud.Pitch(8, 6))
        self.assertEqual(p, mud.Pitch('G#6'))
        self.assertEqual(p, mud.Pitch('Ab6'))

    def test_strip_octave(self):
        self.assertEqual(mud.Pitch('D4').strip_octave(), mud.Pitch('D'))
        self.assertEqual(mud.Pitch('C#', 3).strip_octave(), mud.Pitch('C#'))

    def test_from_music21(self):
        pitch_strs = {'G#4', 'C7'}
        for pstr in pitch_strs:
            mu21p = mu.pitch.Pitch(pstr)
            mudp = mud.Pitch(pstr)
            self.assertEqual(mud.Pitch.from_music21(mu21p), mudp)

@unittest.skip("deprecated")
class TestDuration(unittest.TestCase):
    def test_quantized(self):
        d = mud.Duration(2)
        self.assertTrue(d.is_quantized())
        self.assertEqual(d, mud.Duration(2, quantized=True))
        self.assertEqual(d, mud.Duration(2.0))
        self.assertAlmostEqual(d.in_beats(), 2.0)
        self.assertEqual(d.duration_label(), 10)
        self.assertAlmostEqual(d.resolution(), 1/16.0)

    def test_unquantized(self):
        d = mud.Duration(2.3, quantized=False)
        self.assertNotEqual(d, mud.Duration(2.3, quantized=True))
        self.assertAlmostEqual(d.in_beats(), 2.3)
        self.assertFalse(d.is_quantized())
        with self.assertRaises(ValueError):
            d.duration_label()

        (q, error) = d.as_quantized()
        self.assertFalse(d.is_quantized())
        self.assertTrue(q.is_quantized())
        self.assertNotEqual(d, q)
        self.assertAlmostEqual(q.in_beats(), 2.0)
        self.assertAlmostEqual(error, 0.3)

        d.quantize()
        self.assertEqual(d, q)
    
    def test_label_init(self):
        pass

class TestTime(unittest.TestCase):
    def test_quantized(self):
        t = mud.Time(2.0, resolution=1/8.0)
        self.assertTrue(t.is_quantized())
        self.assertEqual(t, mud.Time(2.0, resolution=1/8.0))
        self.assertEqual(t, mud.Time(2.0, resolution=1/4.0))
        self.assertNotEqual(t, mud.Time(4.0, resolution=1/4.0))
        self.assertNotEqual(t, mud.Time(1.0, resolution=1/8.0))
        self.assertAlmostEqual(t.in_beats(), 2.0)
        self.assertEqual(t.in_resolution_steps(), 16)
        
    def test_zero(self):
        t = mud.Time(0.0, resolution=1/16.0)
        self.assertTrue(t.is_quantized())
        self.assertAlmostEqual(t.resolution(), 1/16.0)
        self.assertEqual(t, mud.Time(0.0))
        self.assertEqual(t, mud.Time(0.0, resolution=1.0))
        self.assertAlmostEqual(t.in_beats(), 0.0)
        self.assertEqual(t.in_resolution_steps(), 0)

    def test_copy(self):
        t = mud.Time(2.0)
        t2 = mud.Time(t)
        self.assertEqual(t, t2)
        self.assertAlmostEqual(t.in_beats(), t2.in_beats())
        self.assertEqual(t.in_resolution_steps(), t2.in_resolution_steps())

    def test_unquantized(self):
        pass

class TestNote(unittest.TestCase):
    def test(self):
        n = mud.Note('G#6', 0.5)

        self.assertEqual(n.pitch().relative_pitch(), 8)
        self.assertEqual(n.pitch().octave(), 6)
        self.assertEqual(n.pitch().name(), 'Ab6')
        self.assertEqual(n.pitch(), mud.Pitch(8, 6))

        self.assertEqual(n.duration(), mud.Time(0.5))
        self.assertTrue(n.duration().is_quantized())
        self.assertAlmostEqual(n.duration().in_beats(), 0.5)

    def test_unpack(self):
        n = mud.Note('Ab2', 4)
        (p, d) = n
        self.assertEqual(p.relative_pitch(), mud.Pitch.str_to_relative_pitch['Ab'])
        self.assertEqual(p.octave(), 2)
        self.assertAlmostEqual(d.in_beats(), 4.0)

    def test_edit_members(self):
        n = mud.Note('C1', mud.Time(0.55, resolution=None))

        self.assertEqual(n.pitch().name(), 'C1')
        n.set_pitch(mud.Pitch('C2'))
        self.assertEqual(n.pitch().name(), 'C2')

        self.assertFalse(n.duration().is_quantized())
        self.assertAlmostEqual(n.duration().in_beats(), 0.55)

        err = n.duration().quantize()

        self.assertAlmostEqual(err, 0.55 - 0.5)
        self.assertAlmostEqual(err, 0.55 - n.duration().in_beats())
        self.assertEqual(n.duration(), mud.Time(0.5))

class TestRest(unittest.TestCase):
    def test(self):
        r = mud.Rest(0.25)
        self.assertEqual(r.pitch(), None)
        self.assertAlmostEqual(r.duration().in_beats(), 0.25)
        self.assertEqual(r, mud.Rest(0.251))

if __name__ == '__main__':
    unittest.main()