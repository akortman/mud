from ..notation import Pitch

_relative_pitches_all = [
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
        self._values_to_labels, self._num_labels = _make_pitch_labels(octave_range, rpitches)
        self._labels_to_values = {value: key for key, value in self._values_to_labels.items()}

    @property
    def num_labels(self):
        return self._num_labels

    def get_label_of(self, pitch):
        p = Pitch(pitch)
        try:
            return self._values_to_labels[p]
        except KeyError:
            raise ValueError("Pitch {} does not have a valid label", p)

    def get_value_of(self, label):
        try:
            return self._labels_to_values[int(label)]
        except KeyError:
            raise ValueError("Label {} does is not associated with a pitch", int(label))

class RelativePitchLabels(Labels):
    def __init__(self, rpitches='all'):
        '''
        Create a set of relative pitch labels.
        rpitches should be 'all' or an iterable of allowed pitches (or strings directly convertible to Pitches.)

        '''
        labels_list = _relative_pitches_all if rpitches == 'all' else rpitches
        for pitch in labels_list:
            if Pitch(pitch).octave() is not None:
                raise ValueError('Pitches provided to RelativePitchLabels must not have octave markers: {}'.format(pitch))
        self._labels_to_values = {i: Pitch(pitch) for i, pitch in enumerate(labels_list)}
        self._values_to_labels = {pitch: label for label, pitch in self._labels_to_values.items()}
        self._num_labels = len(self._labels_to_values.keys())

    @property
    def num_labels(self):
        return self._num_labels

    def get_label_of(self, pitch):
        p = Pitch(pitch)
        if p.octave() is not None:
            raise ValueError('Pitches provided to RelativePitchLabels must not have octave markers: {}'.format(pitch))
        try:
            return self._values_to_labels[p]
        except KeyError:
            raise ValueError("Pitch {} does not have a valid label", p)

    def get_value_of(self, label):
        try:
            return self._labels_to_values[int(label)]
        except KeyError:
            raise ValueError("Label {} does is not associated with a pitch", int(label))