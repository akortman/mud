from ..piece import Piece

class EventData(object):
    def __init__(self, event, formatter):
        self.vec = formatter.make_vector(event)
        self.labels = formatter.make_labels(event)

class TimeSliceData(object):
    def __init__(self, timeslice, formatter, discard_rests=False):
        is_rest = (discard_rests and all(event.is_rest() for event in timeslice))
        if is_rest:
            self.events = []
        else:
            self.events = [EventData(e, formatter) for e in timeslice.sliced_events()]

class BarData(object):
    def __init__(self, bar, formatter, slice_resolution, discard_rests=False):
        self.timeslices = [TimeSliceData(ts, formatter, discard_rests)
                           for ts in bar.generate_slices(slice_resolution)]

class PieceData(object):
    '''
    Structured like a mud.Piece, but contains formatted data for the events in a piece
    (i.e. vectors/matrices and labels).
    Designed purely for iterating over the vectors/labels during training;
    anything more complicated than that should be done to a mud.Piece.
    '''
    def __init__(self, piece, formatter, slice_resolution, discard_rests=False):
        if isinstance(piece, self.__class__):
            raise NotImplementedError('Can\'t copy PieceData yet')
        elif not isinstance(piece, Piece):
            raise ValueError('PieceData is constructed from a Piece')
        
        self.bars = []
        for bar in piece.bars():
            fmt_bar = BarData(bar, formatter, slice_resolution, discard_rests)
            self.bars.append(fmt_bar)

