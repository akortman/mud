'''
Usually, you want to restrict a dataset to a particular kind of Piece,
e.g.  4/4 time.
This module provides implementations of some predicate functions to use
as filters.
'''

def failure_reason(filter):
    if isinstance(filter, PieceFilter):
        return filter.why()
    return f"Failed on testing {filter.type}: filter"

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

    def why(self):
        return f"Unspecified rejection criteria ({type(self)})"

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
        
    def why(self):
        return f"Not atomic slicable with resolution {self._slice_resolution}"

class NotesWithinRange(PieceFilter):
    '''
    Tests whether all notes are within a given note range.
    '''
    def __init__(self, octave_range):
        raise NotImplementedError

    def test(self, piece):
        raise NotImplementedError
        
    def why(self):
        return f"Notes outside of range"

class BarLengthIs(PieceFilter):
    '''
    Tests whether the pieces are in the given time signatures.
    '''
    def __init__(self, bar_length):
        self._bar_length = bar_length

    def test(self, piece):
        for bar in piece.bars():
            if bar.length().in_beats() != self._bar_length:
                return False
        return True
        
    def why(self):
        return f"Bar length not {self._bar_length}"