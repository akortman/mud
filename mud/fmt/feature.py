'''
Utility classes to mark vector features.
Each class takes an Event and generates a subvector, which are then concatenated by a vector builder.
'''

import numpy as np
from .binary_vector import binvec
from . import label

class Feature(object):
    def dim(self):
        return 0

    def make_subvector(self, event):
        return np.zeros(0)

class IsNote(Feature):
    def __init__(self):
        pass

    def dim(self):
        return 1

    def make_subvector(self, event):
        if event.is_note():
            return np.ones(1)
        else:
            return np.zeros(1)

class IsRest(Feature):
    def __init__(self):
        pass

    def dim(self):
        return 1

    def make_subvector(self, event):
        if event.is_rest():
            return np.ones(1)
        else:
            return np.zeros(1)

class NotePitch(Feature):
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

class NoteRelativePitch(Feature):
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