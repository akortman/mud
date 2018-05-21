'''
A Piece is an entire piece of music and it's component events.
'''

import music21 as mu
from .notation import Pitch, Note, Rest, Time
from .span import Span
from .event import Event

class Piece(object):
    def __init__(self, piece=None, discard_rests=False):
        self.init_empty()
        if piece is None:
            return
        elif type(piece) is str:
            self.load_file(piece)
        else:
            raise NotImplementedError('currently Piece only supports loading from file or empty initialization')

        if discard_rests:
            self.discard_rests()

    def init_empty(self, name=None):
        self._bars = []
        self._tonic = None
        self._key_mode = None
        self._name = name

    def load_file(self, path, save_key=False, transpose_to=None):
        s = mu.converter.parse(path)
        return self.from_music21_stream_inplace(s, save_key, transpose_to, name=path)

    @classmethod
    def from_music21_stream(cls, s, save_key=False, transpose_to=None, name=None):
        p = cls()
        p.from_music21_stream_inplace(s, save_key, transpose_to, name)
        return p

    def from_music21_stream_inplace(self, s, save_key=False, transpose_to=None, name=None):
        self.init_empty(name=name)
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
            for elem in m.notesAndRests:
                if elem.isNote:
                    event_data = Note(elem.nameWithOctave, elem.duration.quarterLength)
                else:
                    event_data = Rest(elem.duration.quarterLength)
                events.append(Event(event_data, Time(elem.offset)))
            
            span = Span(events, offset=m.offset)
            self._bars.append(span)

        return self

    def to_music21_stream(self, time_sig=None):
        s = mu.stream.Stream()
        if time_sig is not None:
            s.timeSignature = mu.meter.TimeSignature(time_sig)

        # music21 appends a quarter note rest at the start of the MIDI for some reason.
        # To make it line up nicely in a MIDI editor, we add an initial rest.
        #s.append(mu.note.Rest(quarterLength=3))

        #s.append(mu.note.Note(note.pitch, quarterLength=note.beats))
        #s.append(mu.note.Rest(quarterLength=note.beats))
        for span in self._bars:
            for event in span:
                if event.is_note():
                    ev_mu = mu.note.Note(event.pitch().name())
                else:
                    ev_mu = mu.note.Rest()
                ev_mu.quarterLength = event.duration().in_beats()
                ev_mu.offset = span.offset().in_beats() + event.time().in_beats()
                s.append(ev_mu)
        return s

    def save(self, f, file_format='midi'):
        s = self.to_music21_stream()
        s.write(file_format, f)
        
    @classmethod
    def from_spans(cls, *spans):
        p = cls()
        p.build_from_spans(*spans)
        return p

    def build_from_spans(self, *spans):
        # TODO: Rename
        self.init_empty()
        for bar in spans:
            assert isinstance(bar, Span), 'please provide arguments as all `mud.Span`s'
        self._bars.extend(spans)

    def as_span(self):
        return Span.overlay(*self._bars)

    def events(self):
        s = self.as_span()
        return s.__iter__()

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
    
    def transpose_tonic_to(self, pitch):
        if type(pitch) is not Pitch:
            pitch = Pitch(pitch)
        raise NotImplementedError
    
    def quantize_events(self, max_error=None):
        for bar in self._bars:
            for event in bar:
                event.unwrap().duration().quantize()
                event.time().quantize()

    def discard_rests(self):
        for span in self._bars:
            span.discard_rests()

    def pprint(self):
        print('Piece: {}'.format('' if self._name is None else self._name))
        if self._tonic is not None:
            print('    tonic: {}'.format(self._tonic))
        if self._key_mode is not None:
            print('    mode: {}'.format(self._key_mode))
        for i, bar in enumerate(self._bars):
            print('    {{Bar {}}} ({} to {}):'.format(i, bar.offset(), bar.offset() + bar.length()))
            for j, event in enumerate(bar):
                print('        {{Event {}}} {}'.format(event.time().in_beats(), event.unwrap()))

    def pretty_description(self):
        pad = '    '
        s = ''
        s += 'mud.Piece[\n'
        s += pad + 'tonic: {},\n'.format(self._tonic)
        s += pad + 'mode: {},\n'.format(self._key_mode)
        for i, bar in enumerate(self._bars):
            s += pad + '[{}] {},\n'.format(i, str(bar))
        s += ']\n'
        return s

    @property
    def name(self):
        return '' if self._name is None else self._name
    
    def __str__(self):
        return self.pretty_description()

    def __repr__(self):
        return self.__str__()