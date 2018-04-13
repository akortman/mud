from ..notation import Pitch

_relative_pitches_all = relative_pitch_to_str = [
    'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'
]

def _make_pitch_labels(octave_range, rpitches='all'):
    if rpitches == 'all':
        rpitches = _relative_pitches_all
    if len(rpitches) <= 0:
        raise ValueError('must provide valid list of pitches for pitch labels')
    labels = {}
    next_label = 0
    for octave in range(octave_range[0], octave_range[1] + 1):
        for pitch in rpitches:
            labels[Pitch(pitch, octave)] = next_label
            next_label += 1
    return labels, next_label

class Labels(object):
    pass

class PitchLabels(Labels):
    def __init__(self, octave_range, rpitches='all'):
        self._labels, self._num_labels = _make_pitch_labels(octave_range, rpitches)
        self._values = {value: key for key, value in self._labels.items()}

    def __setitem__(self, key, item):
        raise NotImplementedError
        # It's not clear what this means for num_labels,
        # so it's disabled for now.
        self._labels[Pitch(key)] = int(item)
        self._values[int(item)] = Pitch(key)

    @property
    def num_labels(self):
        return self._num_labels

    def __getitem__(self, key):
        return self._labels[Pitch(key)]

    def get_label_of(self, pitch):
        p = Pitch(pitch)
        try:
            return self._labels[p]
        except KeyError:
            raise ValueError("Pitch {} does not have a valid label", p)

    def get_value_of(self, label):
        try:
            return self._values[int(label)]
        except KeyError:
            raise ValueError("Label {} does is not associated with a pitch", int(label))