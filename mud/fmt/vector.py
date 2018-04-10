'''
Utilities for building feature vectors from notes.
'''

import feature
import numpy as np
from ..event import Event

class VectorBuilder(object):
    def make_vector(self, obj):
        pass

class EventVectorBuilder(VectorBuilder):
    '''
    Class that builds vectors from Events.
    '''
    def __init__(self, features):
        self._features = features
        self._vec_len = sum(f.dim() for f in features)

    def dim(self):
        return sum([f.dim() for f in self._features])

    def make_vector(self, event):
        if not isinstance(event, Event):
            raise ValueError('EventVectorBuilder only formats Events')
        vecs = [feature.make_subvector(event) for feature in self._features]
        return np.concatenate(vecs)


