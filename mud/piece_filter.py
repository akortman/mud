'''
Usually, you want to restrict a dataset to a particular kind of Piece,
e.g.  4/4 time.
This module provides implementations of some predicate functions to use
as filters.
'''

class PieceFilter(object):
    '''
    Generic filter object.
    '''
    def __init__(self):
        raise NotImplementedError

    def test(self, piece):
        raise NotImplementedError

    def __call__(self, piece):
        return self.test(piece)

class AtomicSlicable(PieceFilter):
    '''
    Tests whether all events in a piece are contained in atomic slices
    when sliced to a given resolution.
    '''
    def __init__(self, slice_resolution):
        self._slice_resolution = slice_resolution

    def test(self, piece):
        for bar in piece.bars():
            for ts in bar.generate_slices(self._slice_resolution):
                if not ts.is_atomic_slice():
                    return False
        return True

class NotesWithinRange(PieceFilter):
    '''
    Tests whether all notes are within a given note range.
    '''
    def __init__(self, octave_range):
        raise NotImplementedError

    def test(self, piece):
        raise NotImplementedError

class TimeSignature(PieceFilter):
    '''
    Tests whether the pieces are in the given time signatures.
    '''
    def __init__(self, *time_signatures):
        raise NotImplementedError

    def test(self, piece):
        raise NotImplementedError