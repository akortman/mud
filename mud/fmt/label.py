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
    @property
    def identifier(self):
        ''' returns a unique string identifier that can
            be used to retrieve the labeller later. '''
        try:
            return self._identifier
        except AttributeError:
            return None



class PitchLabels(Labels):
    def __init__(self, octave_range, include_rest=False, rpitches='all'):
        self._identifier = 'Pitch'
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
        self._identifier = 'RelativePitch'
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

''' untested '''
class OctaveLabels(Labels):
    def __init__(self, octave_range, saturate=False):
        self._identifier = 'Octave'
        self._octave_range = octave_range
        self._num_octaves = 1 + max(octave_range) - min(octave_range)
        self._saturate = saturate

    @property
    def num_labels(self):
        return self._num_octaves

    def get_event_label(self, event, **kwargs):
        p = event.pitch()
        if p is None:
            return None
        return self.get_octave_label(p.octave())

    def get_octave_label(self, octave):
        if octave < min(self._octave_range):
            if self._saturate: return min(self._octave_range)
            return None
        if octave > max(self._octave_range):
            if self._saturate: return max(self._octave_range)
            return None
        return octave - min(self._octave_range)

    def get_value_of(self, label):
        if label < 0 or label >= self._num_octaves:
            return None
        return label + min(self._octave_range)

class IsNote(Labels):
    def __init__(self):
        self._identifier = 'IsNote'
        
    @property
    def num_labels(self):
        return 2
        
    def get_event_label(self, event, **kwargs):
        return int(event.is_note())

class IsRest(Labels):
    def __init__(self):
        self._identifier = 'IsRest'
        
    @property
    def num_labels(self):
        return 2
        
    def get_event_label(self, event, **kwargs):
        return int(event.is_rest())

class ContinuingPreviousEventLabel(Labels):
    def __init__(self):
        self._identifier = 'ContinuingPreviousEvent'
        
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
        self._identifier = 'ContinuesNextEvent'
        
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

class SpanPosition(Labels):
    '''
    Labels the position of an event within a span.
    '''
    def __init__(self, resolution, span_length):
        self._identifier = 'SpanPosition'
        self._resolution = resolution
        self._num_steps = int(round(span_length / resolution))

    @property
    def num_labels(self):
        return self._num_steps
        
    def get_event_label(self, event, **kwargs):
        pos_label = int(round(event.time().in_beats() / self._resolution))
        if pos_label >= self._num_steps:
            raise ValueError
        return pos_label

class NoteLength(Labels):
    '''
    Labels the position of an event within a span.
    '''
    def __init__(self, resolution, max_length, saturate=True):
        self._identifier = 'NoteLength'
        self._resolution = resolution
        self._saturate = saturate
        self._num_steps = int(round(max_length / resolution))

    @property
    def num_labels(self):
        return self._num_steps
        
    def get_event_label(self, event, **kwargs):
        len_label = int(round(event.duration().in_beats() / self._resolution))
        if len_label >= self._num_steps:
            if not self._saturate:
                raise ValueError
            len_label = self._num_steps - 1
        return len_label

class BooleanFlag(Labels):
    '''
    Flags with a label of 1 if flag_name=True, otherwise 0
    '''
    def __init__(self, flag_name, identifier=None):
        self._identifier = identifier if identifier is not None else f'{flag_name}_BooleanFlag'
        self.flag_name = flag_name
    
    @property
    def num_labels(self):
        return 2
        
    def get_event_label(self, event, **kwargs):
        if self.flag_name in kwargs and kwargs[self.flag_name]:
            return 1
        return 0

# Helper functions
def StartOfSequence():
    return BooleanFlag('sos')
def EndOfSequence():
    return BooleanFlag('eos')