'''
A Piece is an entire piece of music and it's component events.
'''

import music21 as mu
from Notation import Pitch, Duration, Note, Rest
from Span import Span
from Event import Event

class Piece(object):
    def __init__(self, piece=None):
        self.init_empty()
        if piece is None:
            return
        elif type(piece) is str:
            self.load_file(piece)
        else:
            raise NotImplementedError('currently Piece only supports loading from file or empty initialization')

    def init_empty(self):
        self._bars = []
        self._tonic = None
        self._key_mode = None

    def load_file(self, path, save_key=False, transpose_to=None):
        s = mu.converter.parse(path)
        return self.from_music21_stream(s, save_key, transpose_to)

    def from_music21_stream(self, s, save_key=False, transpose_to=None):
        self.init_empty()
        s = s.flat

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
            transpose_to = Pitch(transpose_to)
            s = s.transpose(transpose_interval, mu.pitch.Pitch(Pitch(transpose_to).name()))

        # Ensure the stream has bars
        if (not s.hasMeasures()):
            s.makeMeasures(inPlace=True)

        # Convert the music21 stream, each bar becomes a mud.Span
        measures = s.getElementsByClass('Measure')
        for m in measures:
            events = []
            span_offset = Duration(m.offset)
            for elem in m.notesAndRests:
                if elem.isNote:
                    event_data = Note(elem.nameWithOctave, elem.duration.quarterLength)
                else:
                    event_data = Rest(elem.duration.quarterLength)
                events.append(Event(event_data,
                                    Duration(elem.offset - span_offset.in_beats())))
            
            span = Span(events, offset=span_offset)
            self._bars.append(span)

        return self

    def events(self):
        for bar in self._bars:
            for event in bar:
                yield event

    def count_events(self):
        return sum(b.num_events() for b in self._bars)

    def num_bars(self):
        return len(self._bars)

    def length_in_beats(self):
        return sum(b.length() for b in self._bars)

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