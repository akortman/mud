'''
Music notation-related classes.
'''

import copy

class Pitch(object):
    '''
    A musical pitch, i.e. C, Bb4.
    May or may not have an associated octave value.
    '''
    str_to_relative_pitch = {
        'C':   0, 'C#': 1, 'Db':  1, 'D':   2,
        'D#':  3, 'Eb': 3, 'E':   4, 'F':   5,
        'F#':  6, 'Gb': 6, 'G':   7, 'G#':  8,
        'Ab':  8, 'A':  9, 'A#': 10, 'Bb': 10,
        'B':  11,
        # music21 uses '-' for flats, so we need to support this for conversions.
        'D-':  1, 'E-': 3, 'G-':  6, 'A-':  8,
        'B-': 10,
    }

    relative_pitch_to_str = [
        'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'
    ]

    def __init__(self, pitch, octave=None):
        if (octave is not None) and (type(octave) is not int):
            raise ValueError('octave argument must be None or int')

        if (type(octave) is int) and (octave < 0):
            raise ValueError('octave must be None or >= 0')
            
        if type(pitch) is Pitch:
            if octave is not None:
                raise ValueError('If Pitch is made as a copy, it can\'t have an octave argument.')
            self._relative_pitch = pitch._relative_pitch
            self._octave = pitch._octave

        elif type(pitch) is str:
            (self._relative_pitch, self._octave) = Pitch.pitch_string_to_pitch_octave_pair(pitch)
            # If the parsed string has an octave value AND we were given an octave value, raise an error.
            if (octave is not None) and (self._octave is not None):
                raise ValueError('provided note string has octave information, but octave information was also provided using the octave argument')
            if self._octave is None: self._octave = octave
        elif type(pitch) is int:
            if pitch < 0 or pitch > 11: raise ValueError('pitch must be between 0 and 11 (inclusive), use octave argument to give octave info')
            self._relative_pitch = pitch
            self._octave = octave

    def octave(self):
        return self._octave

    def midi_pitch(self):
        if self._octave is None: raise ValueError('Pitches without an octave don\'t have a midi absolute pitch')
        return Pitch.to_midi_pitch(self._relative_pitch, self._octave)

    def relative_pitch(self):
        return self._relative_pitch

    def name(self):
        if self._octave is None:
            return self.__class__.relative_pitch_to_str[self._relative_pitch]
        return '{}{}'.format(self.__class__.relative_pitch_to_str[self._relative_pitch], self._octave)

    def __str__(self):
        return 'Pitch[\'{}\']'.format(self.name())

    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return (self._relative_pitch == other._relative_pitch
                and self._octave == other._octave)

    @classmethod
    def to_midi_pitch(cls, relative_pitch, octave):
        '''
        convert a pitch-octave pair into a midi pitch.
        e.g. C-1 -> 0, C4 -> 60, A0 -> 21
        see: https://en.wikipedia.org/wiki/Scientific_pitch_notation
        '''
        return relative_pitch + (octave + 1) * 12

    @classmethod
    def pitch_string_to_pitch_octave_pair(cls, pitchstr):
        '''
        parse a pitch string into a pitch-octave pair
        the octave part is optional
        '''
        pos = 0
        while (pos < len(pitchstr)) and (not pitchstr[pos].isdigit()):
            pos += 1
        if pos == len(pitchstr):
            pitch_part, octave_part = pitchstr, None
        else:
            pitch_part, octave_part = pitchstr[:pos], pitchstr[pos:]
            assert len(pitch_part) + len(octave_part) == len(pitchstr)
        octave = int(octave_part) if octave_part is not None else None
        pitch = cls.str_to_relative_pitch[pitch_part]
        return pitch, octave

    @classmethod
    def from_music21(cls, pitch):
        return cls('{}{}'.format(pitch.name.replace('-', 'b'), pitch.octave))

class Time(object):
    '''
    A class representing a musical time.
    '''
    def __init__(self, time, resolution=1/float(16)):
        self._resolution = resolution
        self._time = time
        if resolution is not None:
            self.quantize_to(resolution)

    def quantize_to(self, resolution):
        self._resolution = resolution
        self._time = resolution * round(self._time / resolution)

    def resolution(self):
        return self._resolution

    def in_resolution_steps(self):
        if self._resolution is None:
            raise ValueError('Can\'t give number of resolution steps in unquantized Time')
        return self._time / self._resolution

    def in_beats(self):
        return self._time

    def is_quantized(self):
        return self._resolution is not None

    def as_quantized(self, resolution):
        new = copy.copy(self)
        new.quantize_to(resolution)
        return new

    def is_zero(self):
        return abs(self._time) < 0.000001

    def __str__(self):
        if self.is_quantized:
            return 'Duration[{}, resolution={}]'.format(self._time, self.in_resolution_steps())
        return 'Duration[{}]'.format(self._time)

    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if type(other) is not self.__class__:
            return False
        if self._resolution == other._resolution:
            if self._resolution is not None:
                return self.in_resolution_steps() == other.in_resolution_steps()
            return self._time == other._time
        # Take the smallest-resolution of the two times, and quantize them to both.
        res = min(self._resolution, other._resolution)
        a = self.as_quantized(res)
        b = other.as_quantized(res)
        return a.in_resolution_steps() == b.in_resolution_steps()

class Duration(object):
    '''
    A class representing the duration of a musical event.
    Can be quantized or unquantized.
    '''
    # The possible quantized durations (in quarter note lengths).
    quantized_durations = [
        0.0,
        1 / float(16),
        1 / float(8),
        1 / float(6),
        1 / float(4),
        1 / float(3),
        1 / float(2),
        1 / float(1.5),
        1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0
    ]

    def __init__(self, duration, quantized=True, _label=None):
        # If quantized, the stored duration is a label that we can lookup using quantized_durations.
        # otherwise, it's a float
        if type(duration) is str:
            raise NotImplementedError('named durations aren\'t supported yet')
            
        if type(duration) is self.__class__:
            assert _label is None
            self._quantized = duration._quantized
            self._duration = duration._duration
            self._label = duration._label
            if quantized and not duration._quantized:
                self.quantize()
            return

        if _label is not None:
            assert type(_label) is int
            assert duration is None
            assert quantized is True
            self._quantized = True
            self._duration = Duration.quantized_durations[_label]
            self._label = _label
            return
        
        self._quantized = False
        self._duration = float(duration)
        self._label = None
        if quantized:
            self.quantize()
    
    def resolution(self):
        elements = [elem for elem in self.__class__.quantized_durations if elem != 0.0]
        return min(elements)

    def in_beats(self):
        if self._quantized:
            return Duration.quantized_durations[self._label]
        return self._duration
    
    def duration_label(self):
        if not self._quantized:
            raise ValueError('Can\'t get the label of a duration that isn\'t quantized')
        return self._label

    def quantize(self):
        (q, quantize_error) = self.as_quantized()
        self._duration = q._duration
        self._label = q._label
        self._quantized = True
        return quantize_error

    def is_quantized(self):
        return self._quantized

    def as_quantized(self):
        '''
        returns (q, e), where:
            - q is the quantized version of this note, and
            - e is the (floating-point) error between the quantized duration and the original duration,
              in beats (quarter notes).
        The quantized note is the duration in the list of quantized durations that minimized error with
        the current duration.
        '''
        if self._quantized:
            return copy.deepcopy(self)
        def err(a, b):
            return abs(a - b)
        errors = [err(self._duration, dur) for dur in self.__class__.quantized_durations]
        new_duration_label = errors.index(min(errors))
        return (Duration(duration=None, _label=new_duration_label),
                errors[new_duration_label])

    def __str__(self):
        if self._quantized:
            return 'Duration[quantized, duration={}, label={}]'.format(self._duration, self._label)
        return 'Duration[unquantized, duration={}]'.format(self._duration)

    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if type(other) is not self.__class__:
            return False
        if self._quantized != other._quantized:
            return False
        if self._quantized and other._quantized:
            return self._label == other._label
        return self._duration == other._duration

class Note(object):
    def __init__(self, pitch=None, duration=None, note=None, quantized=None):
        if note is not None:
            assert pitch is None and duration is None
            self.set_pitch(note.pitch())
            self.set_duration(note.duration(), quantized=note.duration.is_quantized() if quantized is None else quantized)
        else:
            self.set_pitch(pitch)
            self.set_duration(duration, quantized=True if quantized is None else quantized)

    def pitch(self):
        return self._pitch

    def duration(self):
        return self._duration

    def set_pitch(self, pitch):
        self._pitch = Pitch(pitch)

    def set_duration(self, duration, quantized=True):
        self._duration = Duration(duration, quantized=quantized)

    # The iterator protocol is implemented so you can use `pitch, duration = Note(...)` syntax.
    def __iter__(self):
        return (self._pitch, self._duration).__iter__()

    def __str__(self):
        return 'Note [ \'{}\', {} ]'.format(self._pitch.name(), self._duration.in_beats())

    def __repr__(self):
        return 'Note[{}, {}]'.format(self._pitch, self._duration)

    def __eq__(self, other):
        if type(other) is not self.__class__:
            return False
        return self._pitch == other._pitch and self._duration == other._duration

class Rest(object):
    def __init__(self, duration, quantized=True):
        self.set_duration(duration, quantized=quantized)

    def pitch(self):
        return None

    def duration(self):
        return self._duration

    def set_duration(self, duration, quantized=True):
        self._duration = Duration(duration, quantized=quantized)

    def __str__(self):
        return 'Rest [ {} ]'.format(self._duration.in_beats())

    def __repr__(self):
        return 'Rest[{}]'.format(self._duration)

    def __eq__(self, other):
        if type(other) is not self.__class__:
            return False
        return self._duration == other._duration