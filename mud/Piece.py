'''
A Piece is an entire piece of music and it's component events.
'''

import music21 as mu
from Notation import Pitch
from Span import Span
from Event import Event

class Piece(object):
    def __init__(self, piece=None):
        self._bars = []
        self._tonic = None
        self._key_mode = None
        if type(piece) is str:
            self.load_file(piece)
        else:
            raise NotImplementedError('currently Piece only supports loading from file')

    def load_file(self, path, save_key=False, transpose_to=None):
        s = mu.converter.parse(path).flat

        # Get the key of the piece if required.
        if save_key or transpose_to is not None:
            key = s.analyse('key')
            self._tonic = Pitch.from_music21(key.tonic)
            self._key_mode = key.mode 

        # transpose the piece if requiested.
        if transpose_to is not None:
            if self._key_mode == 'major':
                transpose_interval = mu.interval.Interval(key.tonic)
            elif self._key_mode == 'minor':
                transpose_interval = mu.interval.Interval(key.relative.tonic)
            else:
                raise NotImplementedError
            transpose_to = Pitch
            s = s.transpose(transpose_interval, mu.pitch.Pitch(mud.Pitch(transpose_to).name()))

        # Convert the music21 stream, each bar becomes a mud.Span
        pos = 0
        while True:
            m = s.measure(pos)
            if m is None: break
            
            events = []
            span_offset = Duration(m.offset)
            for elem in m.notesAndRests:
                if elem.isNote:
                    event_data = Note(elem.name, elem.duration.quarterLength)
                else:
                    event_data = Rest(elem.duration.quarterLength)
                events.append(Event(event_data, elem.offset - span_offset))
            
            span = mud.Span(events, offset=span_offset)
            self._bars.append(span)

    def events(self):
        for bar in self._bars:
            for event in bar:
                yield event

    def bars(self):
        return self._bars
    
    def transpose(self, interval):
        if type(interval) is not int:
            raise NotImplementedError('non-int intervals not supported yet')
        raise NotImplementedError
    
    def transpose_tonic_to(self, note):
        if type(note) is not Note:
            note = Note(note)
        raise NotImplementedError
    
    def quantize_events(self, max_error=None):
        for bar in self._bars:
            for event in bar:
                event.unwrap().duration().quantize()
                event.time().quantize()