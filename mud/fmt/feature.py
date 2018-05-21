'''
Utility classes to mark vector features.
Each class takes an Event and generates a subvector, which are then concatenated by a vector builder.
'''

import numpy as np
from .binary_vector import binvec
from . import label
import math

def _pascal_case_to_snake_case(string):
    res = []
    for i, c in enumerate(string):
        if i > 0 and c.istitle():
            res.append('_')
        res.append(c.tolower())
        return ''.join(res)
        
class Feature(object):
    def dim(self):
        raise NotImplementedError

    def make_subvector(self, event, **kwargs):
        raise NotImplementedError

    @property
    def identifier(self):
        try:
            return self._identifier
        except AttributeError:
            return None

    @property
    def arg_name(self):
        try:
            return self._arg_name
        except AttributeError:
            if self.identifier is None: return None
            return _pascal_case_to_snake_case(self.identifier)

class EventFeature(Feature):
    pass

class IsNote(EventFeature):
    def __init__(self):
        self._identifier = 'IsNote'

    def dim(self):
        return 1

    def make_subvector(self, event, **kwargs):
        if event.is_note():
            return np.ones(1)
        else:
            return np.zeros(1)

class IsRest(EventFeature):
    def __init__(self):
        self._identifier = 'IsRest'

    def dim(self):
        return 1

    def make_subvector(self, event, **kwargs):
        if event.is_rest():
            return np.ones(1)
        else:
            return np.zeros(1)

class NotePitch(EventFeature):
    def __init__(self, pitch_labels):
        '''
        Create a note pitch feature.
        'labels' should be a dict that maps pitch strings (without octaves) to labels.
        (labels are integers)
        see: mud.fmt.make_pitch_labels
        '''
        self._identifier = 'NotePitch'
        self._pitch_labels = pitch_labels
        self._dim = pitch_labels.num_labels

    def dim(self):
        return self._dim

    def make_subvector(self, event, **kwargs):
        p = event.pitch()
        if p is None:
            return np.zeros(self._dim)
        label = self._pitch_labels.get_label_of(p)
        return binvec(self._dim, label)

class NoteRelativePitch(EventFeature):
    '''
    Generates feature vectors from an Event.
    Generates a _relative pitch_ vector, i.e. pitch without octave.
    '''
    def __init__(self, pitch_labels=None):
        '''
        Create a note relative pitch feature.
        'labels' should be a dict that maps pitch strings (without octaves) to labels.
        (labels are integers)
        '''
        self._identifier = 'NoteRelativePitch'
        if pitch_labels is None:
            self._pitch_labels = label.RelativePitchLabels()
        else:
            self._pitch_labels = pitch_labels
        if not isinstance(self._pitch_labels, label.RelativePitchLabels):
            raise ValueError("pitch labels in NoteRelativePitch must be mud.fmt.label.RelativePitchLabels")
        self._dim = self._pitch_labels.num_labels
        if self._dim > 12:
            raise ValueError('Feature vector dimension for relative pitch must be 12 or less')

    def dim(self):
        return self._dim

    def make_subvector(self, event, **kwargs):
        try:
            rp = event.pitch().relative_pitch()
        except AttributeError:
            return np.zeros(self._dim)
        label = self._pitch_labels.get_label_of(rp)
        return binvec(self._dim, label)

class NoteOctave(EventFeature):
    '''
    Generates feature vectors marking the labelled octave of a note.
    '''
    def __init__(self, octave_range, saturate=False):
        self._identifier = 'NoteOctave'
        if len(octave_range) != 2 or octave_range[0] > octave_range[1]:
            raise ValueError
        self._octave_range = octave_range
        self._saturate = saturate

    def dim(self):
        return 1 + self._octave_range[1] - self._octave_range[0]

    def _label_of_octave(self, octave):
        if octave < self._octave_range[0]:
            if self._saturate: return self._octave_range[0]
            raise ValueError('octave out of range')
        if octave > self._octave_range[1]:
            if self._saturate: return self._octave_range[1]
            raise ValueError('octave out of range')
        return octave - self._octave_range[0]

    def make_subvector(self, event, **kwargs):
        p = event.pitch()
        if p is None:
            return np.zeros(self.dim())
        label = self._label_of_octave(p.octave())
        return binvec(self.dim(), (label,))

class NoteOctaveContinuous(EventFeature):
    '''
    Generates feature vectors marking the continuous octave of a note.
    This means that rather than a one-hot vector with a 1 marking the octave,
    it's a continuous 1, 2, 3, 4... with dimension 1.
    '''
    def __init__(self, rest_octave_value=0.0):
        self._identifier = 'NoteOctaveContinuous'
        self._rest_octave_value = rest_octave_value

    def dim(self):
        return 1

    def make_subvector(self, event, **kwargs):
        try:
            octave = event.pitch().octave()
        except AttributeError:
            if (self._rest_octave_value is None):
                return None
            octave = self._rest_octave_value
        return np.full((1,), float(octave), dtype='float')

class ContinuingPreviousEvent(EventFeature):
    '''
    Generates feature vectors marking whether this event is a continuation
    of a previous event.
    '''
    def __init__(self):
        self._identifier = 'ContinuingPreviousEvent'

    def dim(self):
        return 1

    def make_subvector(self, event, **kwargs):
        try:
            if not event.is_note_start():
                return np.ones(1)
        except AttributeError:
            pass
        return np.zeros(1)

class ContinuesNextEvent(EventFeature):
    '''
    Generates feature vectors marking whether this event is continued by a
    subsequent event.
    '''
    def __init__(self):
        self._identifier = 'ContinuesNextEvent'

    def dim(self):
        return 1

    def make_subvector(self, event, **kwargs):
        try:
            if not event.is_note_end():
                return np.ones(1)
        except AttributeError:
            pass
        return np.zeros(1)

class SpanPosition(EventFeature):
    '''
    Flags the position within the containing span.
    (Pieces are by default broken up into bar spans.)
    '''
    def __init__(self, resolution, span_length):
        self._identifier = 'SpanPosition'
        self._resolution = resolution
        self._num_steps = int(round(span_length / resolution))

    def dim(self):
        return self._num_steps

    def make_subvector(self, event, **kwargs):
        pos_label = int(round(event.time().in_beats() / self._resolution))
        if pos_label >= self._num_steps:
            raise ValueError
        return binvec(self.dim(), (pos_label,))

class NoteLength(EventFeature):
    '''
    Labels the length of a note, divided into a given resolution.
    '''
    def __init__(self, resolution, max_length, saturate=True):
        self._identifier = 'SpanPosition'
        self._resolution = resolution
        self._saturate = saturate
        self._num_steps = int(round(max_length / resolution))

    def dim(self):
        return self._num_steps

    def make_subvector(self, event, **kwargs):
        len_label = int(round(event.duration().in_beats() / self._resolution))
        if len_label >= self._num_steps:
            if not self._saturate:
                raise ValueError
            len_label = self._num_steps - 1
        return binvec(self.dim(), (len_label,))

class BooleanFlag(EventFeature):
    '''
    Flags with a 1 if flag_name=True in additional args.
    '''
    def __init__(self, flag_name, identifier=None):
        self._identifier = identifier if identifier is not None else f'{flag_name}_BooleanFlag'
        self.flag_name = flag_name

    def dim(self):
        return 1

    def make_subvector(self, event, **kwargs):
        if self.flag_name in kwargs and kwargs[self.flag_name]:
            return np.ones(1)
        return np.zeros(1)

# Helper functions
def StartOfSequence():
    return BooleanFlag('sos')
def EndOfSequence():
    return BooleanFlag('eos')