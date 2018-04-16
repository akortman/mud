import unittest
import mud
import mud.fmt.feature as feature
import mud.fmt.label as label

class TestFmtData(unittest.TestCase):
    def test(self):
        pitch_labels = label.PitchLabels(octave_range=(4, 6))
        formatter = mud.fmt.EventDataBuilder(
            features=(
                feature.IsNote(),
                feature.IsRest(),
                feature.NotePitch(pitch_labels),
            ),
            labels=(
                pitch_labels
            ))

        # TEST INPUT VECTOR CONSTRUCTION
        event = mud.Event(mud.Note('C#4', mud.Time(1.0)), mud.Time(0.0))
        v = formatter.make_vector(event)
        self.assertEqual(v.shape, (12 * 3 + 2,)) # 3 octaves + 1 note indicator + 1 rest indicator
        note_label = pitch_labels.get_label_of('C#4')
        self.assertEqual(note_label, 1)
        for i in range(v.shape[0]):
            if (i == 0                      # The note indicator
                or i == 2 + note_label):    # The pitch marker
                self.assertAlmostEqual(v[i], 1.0)
            else:
                self.assertAlmostEqual(v[i], 0.0)
    
        event = mud.Event(mud.Rest(mud.Time(3.0)), mud.Time(1.0))
        v = formatter.make_vector(event)
        self.assertEqual(v.shape, (12 * 3 + 2,)) # 3 octaves + 1 note indicator + 1 rest indicator
        self.assertEqual(note_label, 1)
        for i in range(v.shape[0]):
            if i == 1:   # note indicator
                self.assertAlmostEqual(v[i], 1.0)
            else:
                self.assertAlmostEqual(v[i], 0.0)