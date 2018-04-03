'''
Music notation-related classes.
'''

note_names_to_pitch_in_octave = {
    'C':   0, 'C#': 1, 'Db':  1, 'D':   2,
    'D#':  3, 'Eb': 3, 'E':   4, 'F':   5,
    'F#':  6, 'Gb': 6, 'G':   7, 'G#':  8,
    'Ab':  8, 'A':  9, 'A#': 10, 'Bb': 10,
    'B':  11
}

pitch_in_octave_to_note_name = [
    'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'
]


def to_midi_pitch(pitch, octave):
    '''
    convert a pitch-octave pair into a midi pitch.
    e.g. C-1 -> 0, C4 -> 60, A0 -> 21
    see: https://en.wikipedia.org/wiki/Scientific_pitch_notation
    '''
    raise NotImplementedError

class Pitch(object):
    '''
    A musical pitch, i.e. C, Bb4.
    May or may not have an associated octave value.
    '''
    def __init__(self, pitch, octave=None):
        if type(pitch) is Pitch:
            self.value = pitch.value
        elif type(pitch) is str:
            self.value = 
        elif type(pitch) is int:
            self.value = pitch

    def octave():
        raise NotImplementedError

    def midi_pitch():
        raise NotImplementedError

    def pitch_in_octave():
        raise NotImplementedError

    def name():
        raise NotImplementedError

    def __str__():
        raise NotImplementedError

    def __repr__():
        raise NotImplementedError

class Note(object):
    def __init__(self, pitch, duration):
        self.pitch = Pitch(pitch)
        self.duration = Duration(pitch)