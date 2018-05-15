'''
Utilities for building feature vectors from notes.
'''

import numpy as np
import enum
from . import feature
from ..event import Event

class OutputLibrary(enum.Enum):
    NUMPY = 1
    TORCH = 2

str_to_lib = {
    'numpy': OutputLibrary.NUMPY,
    'torch': OutputLibrary.TORCH,
}

def _numpy_to_output_library_format(nparray, output_library):
    if output_library is OutputLibrary.NUMPY:
        return nparray
    if output_library is OutputLibrary.TORCH:
        try:
            import torch
            return torch.Tensor(nparray)
        except (ImportError, ModuleNotFoundError):
            raise ValueError('Using output library pytorch, which is could not be imported')
    else:
        raise ValueError('Cannot convert output vector to unsupported format {}'.format(output_library))

class DataBuilder(object):
    def make_vector(self, obj, library=None):
        raise NotImplementedError
        
    def make_labels(self, obj, library=None):
        raise NotImplementedError

class EventDataBuilder(DataBuilder):
    '''
    Class that builds vectors and labels from Events.
    '''
    def __init__(self, features, labels, library=OutputLibrary.NUMPY):
        self._features = features
        self._labels = labels
        self._vec_len = sum(f.dim() for f in features)
        self._output_library = str_to_lib[library] if isinstance(library, str) else library

    def dim(self):
        return self._vec_len

    def _make_numpy_subvectors(self, event, **kwargs):
        return [feature.make_subvector(event, **kwargs) for feature in self._features]

    def _make_numpy_vector(self, event, **kwargs):
        return np.concatenate(self._make_numpy_subvectors(event, **kwargs))

    def _assert_is_event(self, event):
        if not isinstance(event, Event):
            raise ValueError('EventVectorBuilder only formats Events')

    def make_vector(self, event, library=None, **kwargs):
        self._assert_is_event(event)
        return _numpy_to_output_library_format(self._make_numpy_vector(event, **kwargs),
                                               self._output_library if library is None else library)

    def make_labels(self, event, library=None, **kwargs):
        self._assert_is_event(event)
        return tuple(l.get_event_label(event, **kwargs) for l in self._labels)

    def label_value(self, label_identifier, label):
        '''
        Get the value of a label given a particular identifier for a labeller (see `mud.fmt.label`)
        Will throw if there are multiple labellers with the same identifier.
        '''
        labeller = [l for l in self._labels if l.identifier == label_identifier]
        if len(labeller) == 0:
            raise ValueError(f'Labeller \'{label_identifier}\' not found in EventDataBuilder')
        if len(labeller) > 1:
            raise ValueError(f'Ambiguous label identifier; multiple labellers ({len(labeller)}) found for \'{label_identifier}\'')
        labeller = labeller[0]
        return labeller.get_value_of(label)