import numpy as np

def binvec(length, *indices):
    '''
    build a binary vector with the given length, filled with zeros except
    for the values at the indices provided, which are 1.
    '''
    v = np.zeros(length, dtype='float')
    for i in indices:
        v[i] = 1.0
    return v