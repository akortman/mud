import unittest
import mud
import mud.fmt.feature as feature
import mud.fmt.label as label
import numpy as np

note = mud.Event(mud.Note('G7', 2.0), mud.Time(0.0))
rest = mud.Event(mud.Rest(1.0), mud.Time(0.0))

class TestIsNote(unittest.TestCase):
    def test(self):
        f = feature.IsNote()
        self.assertEqual(f.dim(), 1)
        self.assertEqual(f.make_subvector(note).shape, (1,))
        self.assertEqual(f.make_subvector(note), np.ones(1))
        self.assertEqual(f.make_subvector(note)[0], 1)
        self.assertEqual(f.make_subvector(rest).shape, (1,))
        self.assertEqual(f.make_subvector(rest), np.zeros(1))
        self.assertEqual(f.make_subvector(rest)[0], 0)
     
class TestIsRest(unittest.TestCase):
    def test(self):   
        f = feature.IsRest()
        self.assertEqual(f.dim(), 1)
        self.assertEqual(f.make_subvector(note).shape, (1,))
        self.assertEqual(f.make_subvector(note), np.zeros(1))
        self.assertEqual(f.make_subvector(note)[0], 0)
        self.assertEqual(f.make_subvector(rest).shape, (1,))
        self.assertEqual(f.make_subvector(rest), np.ones(1))
        self.assertEqual(f.make_subvector(rest)[0], 1)

class TestNotePitch(unittest.TestCase):
    def test(self):   
        pitch_labels = label.PitchLabels(octave_range=(4, 7))
        f = feature.NotePitch(pitch_labels)
        self.assertEqual(f.dim(), 12 * 4)

        v = f.make_subvector(note)
        self.assertEqual(v.shape, (12 * 4,))
        note_label = pitch_labels.get_event_label(note)
        for i in range(12 * 4):
            self.assertEqual(v[i], 1 if i == note_label else 0)
            
        v = f.make_subvector(rest)
        self.assertEqual(v.shape, (12 * 4,))
        for i in range(12 * 4):
            self.assertEqual(v[i], 0)
        
class TestNoteRelativePitch(unittest.TestCase):
    def test(self):   
        rpitch_labels = label.RelativePitchLabels()
        f = feature.NoteRelativePitch(rpitch_labels)
        self.assertEqual(f.dim(), 12)

        v = f.make_subvector(note)
        self.assertEqual(v.shape, (12,))
        note_label = rpitch_labels.get_event_label(note)
        for i in range(12):
            self.assertEqual(v[i], 1 if i == note_label else 0)
            
        v = f.make_subvector(rest)
        self.assertEqual(v.shape, (12,))
        for i in range(12):
            self.assertEqual(v[i], 0)

class TestNoteOctave(unittest.TestCase):
    def test(self):  
        f = feature.NoteOctave((6, 7))
        self.assertEqual(f.dim(), 2)

        v = f.make_subvector(note)
        self.assertEqual(v.shape, (2,))
        self.assertAlmostEqual(v[0], 0.0)
        self.assertAlmostEqual(v[1], 1.0)

        v = f.make_subvector(rest)
        self.assertEqual(v.shape, (2,))
        self.assertAlmostEqual(v[0], 0.0)
        self.assertAlmostEqual(v[0], 0.0)

class TestNoteOctaveContinuous(unittest.TestCase):
    def test(self):  
        f = feature.NoteOctaveContinuous()
        self.assertEqual(f.dim(), 1)

        v = f.make_subvector(note)
        self.assertEqual(v.shape, (1,))
        self.assertAlmostEqual(v[0], 7.0)

        v = f.make_subvector(rest)
        self.assertEqual(v.shape, (1,))
        self.assertAlmostEqual(v, 0.0)

class TestContinuingPreviousEvent(unittest.TestCase):
    def test(self):
        f = feature.ContinuingPreviousEvent()
        self.assertEqual(f.dim(), 1)
        
        event = mud.Event(mud.Note('C#4', mud.Time(4.0)), mud.Time(0.0))
        v = f.make_subvector(event)
        self.assertEqual(v.shape, (1,))
        self.assertAlmostEqual(v[0], 0.0)

        # middle slice
        sliced_event = mud.SlicedEvent((2.0, 3.0), event)
        v = f.make_subvector(sliced_event)
        self.assertEqual(v.shape, (1,))
        self.assertAlmostEqual(v[0], 1.0)

        # no slice
        sliced_event = mud.SlicedEvent((0.0, 4.0), event)
        v = f.make_subvector(sliced_event)
        self.assertEqual(v.shape, (1,))
        self.assertAlmostEqual(v[0], 0.0)

        # slice to end
        sliced_event = mud.SlicedEvent((2.0, 4.0), event)
        v = f.make_subvector(sliced_event)
        self.assertEqual(v.shape, (1,))
        self.assertAlmostEqual(v[0], 1.0)

class TestContinuesNextEvent(unittest.TestCase):
    def test(self):
        f = feature.ContinuesNextEvent()
        self.assertEqual(f.dim(), 1)
        
        event = mud.Event(mud.Note('A6', mud.Time(4.0)), mud.Time(0.0))
        v = f.make_subvector(event)
        self.assertEqual(v.shape, (1,))
        self.assertAlmostEqual(v[0], 0.0)

        # middle slice
        sliced_event = mud.SlicedEvent((2.0, 3.0), event)
        v = f.make_subvector(sliced_event)
        self.assertEqual(v.shape, (1,))
        self.assertAlmostEqual(v[0], 1.0)

        # no slice
        sliced_event = mud.SlicedEvent((0.0, 4.0), event)
        v = f.make_subvector(sliced_event)
        self.assertEqual(v.shape, (1,))
        self.assertAlmostEqual(v[0], 0.0)

        # slice from start
        sliced_event = mud.SlicedEvent((0.0, 3.5), event)
        v = f.make_subvector(sliced_event)
        self.assertEqual(v.shape, (1,))
        self.assertAlmostEqual(v[0], 1.0)

class TestBooleanFlag(unittest.TestCase):
    def test(self):
        f = feature.BooleanFlag('flag')
        self.assertEqual(f.dim(), 1)
        
        event = mud.Event(mud.Note('A6', mud.Time(4.0)), mud.Time(0.0))

        v = f.make_subvector(event)
        self.assertEqual(v.shape, (1,))
        self.assertAlmostEqual(v[0], 0.0)

        v = f.make_subvector(event, flag=False)
        self.assertEqual(v.shape, (1,))
        self.assertAlmostEqual(v[0], 0.0)

        v = f.make_subvector(event, flag=True)
        self.assertEqual(v.shape, (1,))
        self.assertAlmostEqual(v[0], 1.0)


