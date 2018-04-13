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

def _numpy_to_output_library_format(nparray, output_library):
    if output_library is OutputLibrary.NUMPY:
        return nparray
    if output_library is OutputLibrary.TORCH:
        try:
            import torch
            return torch.Tensor(nparray)
<<<<<<< HEAD
        except (ImportError, ModuleNotFoundError):
=======
        except ImportError, ModuleNotFoundError:
>>>>>>> 7817101a3e0e3f7358f8fca2533cd6cee1320bd6
            raise ValueError('Using output library pytorch, which is could not be imported')
    else:
        raise ValueError('Cannot convert output vector to unsupported format {}'.format(output_library))

class VectorBuilder(object):
    def make_vector(self, obj):
        pass

class EventVectorBuilder(VectorBuilder):
    '''
    Class that builds vectors from Events.
    '''
    def __init__(self, features, library=OutputLibrary.NUMPY):
        self._features = features
        self._vec_len = sum(f.dim() for f in features)
        self._output_library = library

    def dim(self):
        return self._vec_len

    def _make_numpy_vector(self, event):
        vecs = [feature.make_subvector(event) for feature in self._features]
        return np.concatenate(vecs)

    def make_vector(self, event):
        if not isinstance(event, Event):
            raise ValueError('EventVectorBuilder only formats Events')
        return _numpy_to_output_library_format(self._make_numpy_vector(event), self._output_library)



