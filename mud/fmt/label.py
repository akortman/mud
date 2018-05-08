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
    @property
    def num_labels(self):
        raise NotImplementedError
    def get_event_label(self, event, **kwargs):
        raise NotImplementedError

class PitchLabels(Labels):
    def __init__(self, octave_range, include_rest=False, rpitches='all'):
        self._include_rest = include_rest
        self._values_to_labels, self._num_labels = _make_pitch_labels(octave_range, rpitches)
        if include_rest:
            self._values_to_labels[None] = self._num_labels
            self._num_labels += 1
        self._labels_to_values = {value: key for key, value in self._values_to_labels.items()}

    @property
    def num_labels(self):
        return self._num_labels

    def get_event_label(self, event, **kwargs):
        return self.get_label_of(event.pitch())

    def get_label_of(self, pitch):
        if pitch is None and not self._include_rest:
            return None
        p = Pitch(pitch) if pitch is not None else None
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
    def __init__(self, include_rest=False, rpitches='all'):
        '''
        Create a set of relative pitch labels.
        rpitches should be 'all' or an iterable of allowed pitches (or strings directly convertible to Pitches.)

        '''
        labels_list = _relative_pitches_all if rpitches == 'all' else rpitches
        self._labels_to_values = {i: Pitch(pitch).strip_octave() for i, pitch in enumerate(labels_list)}
        self._num_labels = len(self._labels_to_values.keys())
        self._include_rest = include_rest
        if include_rest:
            self._labels_to_values[self._num_labels] = None
            self._num_labels += 1
        self._values_to_labels = {pitch: label for label, pitch in self._labels_to_values.items()}

    @property
    def num_labels(self):
        return self._num_labels

    def get_event_label(self, event, **kwargs):
        return self.get_label_of(event.pitch())

    def get_label_of(self, pitch):
        if pitch is None and not self._include_rest:
            return None
        p = Pitch(pitch).strip_octave() if (pitch is not None) else None
        try:
            return self._values_to_labels[p]
        except KeyError:
            raise ValueError("Pitch {} does not have a label".format(p))

    def get_value_of(self, label):
        try:
            return self._labels_to_values[int(label)]
        except KeyError:
            raise ValueError("Label {} does is not associated with a pitch".format(int(label)))

class IsNote(Labels):
    def __init__(self):
        pass
        
    @property
    def num_labels(self):
        return 2
        
    def get_event_label(self, event, **kwargs):
        return int(event.is_note())

class IsRest(Labels):
    def __init__(self):
        pass
        
    @property
    def num_labels(self):
        return 2
        
    def get_event_label(self, event, **kwargs):
        return int(event.is_rest())

class ContinuingPreviousEventLabel(Labels):
    def __init__(self):
        pass
        
    @property
    def num_labels(self):
        return 2

    def get_event_label(self, event, **kwargs):
        try:
            if not event.is_note_start():
                return 1
        except AttributeError:
            pass
        return 0

class ContinuesNextEventLabel(Labels):
    def __init__(self):
        pass
        
    @property
    def num_labels(self):
        return 2
        
    def get_event_label(self, event, **kwargs):
        try:
            if not event.is_note_end():
                return 1
        except AttributeError:
            pass
        return 0