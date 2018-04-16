# mud
`mud` (`mu`sic`d`ata) is a music data processing library for deep learning projects.
`mud` is made to simplify the process of converting events in music files into _input
vectors_ and _target labels_, not for musical computation in general (see `music21`, which
`mud` uses, for that). It's also primarily made to fit my (ie @jkortman's) needs, but
anyone is welcome to use/extend it.

When working on deep learning applications to music, I've found data handling code to be
a large amount of work without actually producing any results. This library is an attempt to
make resusable code to perform the work converting music source files (musicxml, MIDI, etc)
into formats ready for use in deep learning frameworks. Currently supported are `numpy`
and `torch`, but most libraries should interface nicely with `numpy`)

## Installation
`mud` is not on pip.

Recommended install is to clone `mud` and then `pip install .` in the base
directory (with setup.py in it). Then `import mud` and continue.

## Features
### Data formatting
Time quantization and time slicing API for finding all events occuring within a particular
time range.
```python
piece = mud.Piece('path/to/piece.musicxml')
# Pieces are represented as a number of Spans.
# Spans are generic subsections of a piece of music.
# However, mud.Piece is stored by default with Spans containing each measure of the piece.
# You can retrieve the entire piece as a single Span using `Piece(...).as_span()`, or
# iterate over events using `for event in piece.events()`.

# If we want to take a look at this, we can do:
piece.pprint()
#   Piece: path/to/piece.musicxml
#       {Bar 0} (Time[0.0, resolution=0.0] to Time[4.0, resolution=32.0]):
#           {Event 0.0} Note [ 'C4', 1.0 ]
#           {Event 0.0} Note [ 'G5', 1.0 ]
#           {Event 1.0} Rest [ 1.0 ]
#           {Event 2.0} Note [ 'C4', 2.0 ]
#           {Event 2.0} Note [ 'A4', 2.0 ]

# Now, to see all events occuring within time 2.5 to 3.0 (in beats/quarter notes):
ts = p.as_span().get_slice((2.5, 3.0))
from pprint import pprint
pprint(ts.raw_events())
#   [Event[Note [ 'C4', 2.0 ], time=Time[2.0, resolution=16.0]],
#    Event[Note [ 'A4', 2.0 ], time=Time[2.0, resolution=16.0]]]

# If we want to iterate through sliced versions of the events, we can use ts.sliced_events(),
# which will also mark whether the event extends before or beyond the slice:
TODO

# It's also useful to check whether any of the contained events are smaller than the slice.
# This is referred to as an 'atomic slice' by `mud`.
if not ts.is_atomic_slice():
    raise 'this won't be raised!'
```

Extensible input/label generation for musical events (currently notes and rests):
```python
import mud
import mud.fmt.label as label
import mud.fmt.feature as feature

pitch_labels = label.PitchLabels(octave_range=(4, 5))
formatter = mud.fmt.EventDataBuilder(
    features=(                            # Feature classes specify part of a vector to produce.
        feature.IsNote(),                 # This EventDataBuilder converts events into binary vectors
        feature.IsRest(),                 # specifying whether the feature is a note or rest, and the
        feature.NotePitch(pitch_labels),  # pitch of the event if in octave ranges 4 to 5 (two octaves).
    ),                                    # These are extensible, you can write your own features.
    labels=(                              # Label classes specify target labels to be produced from each note.
        pitch_labels,                     
    ))
# Now, we can generate a vector for any event (note or rest):
vector = formatter.make_vector(mud.Note('G#4'))
# vector == np.asarray([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,])
# the first 1 is the IsNote flag, the second 1 flags the note as a G#4.
# We can also generate the requested labels from an event:
labels = formatter.make_labels(mud.Note('G#4'))
# labels == (7,)
# G#4 is the 7th pitch in our labels.
# If necessary, further features and labels can be added: durations, note velocity, etc.
```

The idea is to use the time slicing API to subdivide your pieces, then a EventDataBuilder to convert those
into formats ready to use with deep learning models.
