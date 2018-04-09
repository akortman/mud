from ..notation import Pitch

_pitches_all = relative_pitch_to_str = [
    'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'
]

def make_pitch_labels(octave_range, pitches='all'):
    if pitches == 'all':
        pitches = _pitches_all
    if len(pitches) <= 0:
        raise ValueError('must provide valid list of pitches for pitch labels')
    labels = {}
    next_label = 0
    for octave in range(octave_range[0], octave_range[1] + 1):
        for pitch in pitches:
            labels[Pitch(pitch, octave)] = next_label
            next_label += 1
    return labels, next_label