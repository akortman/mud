'''
Utility classes to mark vector features.
Each class takes an Event and generates a subvector, which are then concatenated by a vector builder.
'''

import numpy as np
from .binary_vector import binvec
from . import label

class Feature(object):
    def dim(self):
        raise NotImplementedError

    def make_subvector(self, event):
        raise NotImplementedError

class EventFeature(Feature):
    pass

class IsNote(EventFeature):
    def __init__(self):
        pass

    def dim(self):
        return 1

    def make_subvector(self, event):
        if event.is_note():
            return np.ones(1)
        else:
            return np.zeros(1)

class IsRest(EventFeature):
    def __init__(self):
        pass

    def dim(self):
        return 1

    def make_subvector(self, event):
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
        self._pitch_labels = pitch_labels
        self._dim = pitch_labels.num_labels

    def dim(self):
        return self._dim

    def make_subvector(self, event):
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
        if pitch_labels is None:
            self._pitch_labels = label.RelativePitchLabels()
        else:
            self._pitch_labels = pitch_labels
        if not isinstance(self._pitch_labels, label.RelativePitchLabels):
            raise ValueError("pitch labels in NoteRelativePitch must be mud.fmt.label.RelativePitchLabels")
        self._dim = pitch_labels.num_labels
        if self._dim > 12:
            raise ValueError('Feature vector dimension for relative pitch must be 12 or less')

    def dim(self):
        return self._dim

    def make_subvector(self, event):
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
    def __init__(self, octave_range):
        if len(octave_range) != 2 or octave_range[0] > octave_range[1]:
            raise ValueError
        self._octave_range = octave_range

    def dim(self):
        return 1 + self._octave_range[1] - self._octave_range[0]

    def _label_of_octave(self, octave):
        return octave - self._octave_range[0]

    def make_subvector(self, event):
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
        self._rest_octave_value = rest_octave_value

    def dim(self):
        return 1

    def make_subvector(self, event):
        try:
            octave = event.pitch().octave()
        except AttributeError:
            if (self._rest_octave_value is None):
                return None
            octave = self._rest_octave_value
        return np.full((1,), float(octave), dtype='float')