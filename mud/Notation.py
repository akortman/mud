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
        'B':  11
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
        raise self._relative_pitch

    def name(self):
        if self._octave is None:
            return self.__class__.relative_pitch_to_str[self._relative_pitch]
        return '{}{}'.format(self.__class__.relative_pitch_to_str[self._relative_pitch], self._octave)

    def __str__(self):
        return 'Note[\'{}\']'.format(self.name())

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
        pitch = cls.relative_pitch_to_str.index(pitch_part)
        return pitch, octave

class Duration(object):
    '''
    A class representing a musical duration.
    Can be quantized or unquantized.
    '''
    # The possible quantized durations (in quarter note lengths).
    quantized_durations = [
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
        if _label is not None:
            assert type(_label) is int
            self._quantized = True
            self._duration = Duration.quantized_durations[_label]
            self._label = _label
        else:
            self._quantized = False
            self._duration = float(duration)
            self._label = None
            if quantized:
                self.quantize()

    def duration_in_beats(self):
        if self._quantized:
            return Duration.quantized_durations[self._label]
        return self._duration
    
    def duration_label(self):
        if not self._quantized:
            raise ValueError('Can\'t get the label of a duration that isn\'t quantized')
        return self._label

    def quantize(self):
        (self, quantize_error) = self.as_quantized()
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

    def __eq__(self, other):
        if type(other) is not self.__class__:
            return False
        if self._quantized and other._quantized:
            return self._label == other._label
        return self._duration == other._duration

class Note(object):
    def __init__(self, pitch, duration):
        self._pitch = Pitch(pitch)
        self._duration = Duration(pitch)

    def pitch(self):
        return self._pitch

    def duration(self):
        return self._duration

    # The iterator protocol is implemented so you can use `pitch, duration = Note(...)` syntax.
    def __iter__(self):
        return (self._pitch, self._duration).__iter__()

    def __eq__(self, other):
        return # TODO