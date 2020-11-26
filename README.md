# mud
`mud` (`mu`sic`d`ata) is a music data processing library for deep learning projects.
`mud` is made to simplify the process of converting events in music files into _input
vectors_ and _target labels_, not for musical computation in general (see `music21`, which
`mud` uses, for that). It's also primarily made to fit my (ie @akortman's) needs, but
anyone is welcome to use/extend it.

When working on deep learning applications to music, I've found data handling code to be
a large amount of work without actually producing any results. This library is an attempt to
make resusable code to perform the work converting music source files (musicxml, MIDI, etc)
into formats ready for use in deep learning frameworks. Currently supported are `numpy`
and `torch`, but most libraries should interface nicely with `numpy`)

## Installation
Recommended install is to clone this repo and then `pip install .` in the base
directory (with setup.py in it). Then `import mud` and continue.

## Minimal example
```python
import mud
# Load a piece.
# Pieces are comprised of mud.Span objects.
# By default these spans contain the contents of each bar, but there's no reason
# they can't be different - pieces could be one Span, or have several Spans simultaneously.
piece = mud.Piece('path/to/piece.mxl')

# If we want to look at the internal structure of the piece:
piece.show()
#   Piece: path/to/piece.musicxml
#       {Span 0} (Time[0.0, resolution=0.125, steps=0] to Time[4.0, resolution=0.125, steps=32]):
#           {Event 0.0} Note [ 'C4', 1.0 ]
#           {Event 0.0} Note [ 'G5', 1.0 ]
#           {Event 1.0} Rest [ 1.0 ]
#           {Event 2.0} Note [ 'C4', 2.0 ]
#           {Event 2.0} Note [ 'A4', 2.0 ]

# This piece has a single Span with 5 events. The Span is a bar (4.0 quarter notes long),
# subdivided with a resolution of 0.125 quarter notes. The length of the bar in resolution-sized
# steps is 32.

# If the rest data is unneeded:
piece.discard_rests()
piece.show()
#   Piece: path/to/piece.musicxml
#       {Span 0} (Time[0.0, resolution=0.125, steps=0] to Time[4.0, resolution=0.125, steps=32]):
#           {Event 0.0} Note [ 'C4', 1.0 ]
#           {Event 0.0} Note [ 'G5', 1.0 ]
#           {Event 2.0} Note [ 'C4', 2.0 ]
#           {Event 2.0} Note [ 'A4', 2.0 ]

# Say we have a collection of pieces and want to use them in a machine learning model.
# For each note, we want to produce a feature vector and a set of labels, arranged by piece and by bar.
corpus = mud.Corpus(('path/to/data/*.mxl', 'another/dataset/*.mxl'),
                    discard_rests=True)

# the EventDataBuilder class is used to specify data (vector and label) formats for events.
# (There are other feature and label generators when required, and they are extensible)
from mud.fmt import feature, label
formatter = mud.fmt.EventDataBuilder(
    features=( 
        feature.NoteRelativePitch(),
        feature.NoteLength(resolution=0.25, max_length=2.0)),
    labels=(
        label.RelativePitchLabels(),
        label.NoteLength(resolution=0.25, max_length=2.0)),
    library='torch',
)

# we can now call formatter.make_vector(event) and formatter.make_labels(event)
# to produce the specified vector and labels for any given event (which a mud.Piece
# is made up of).
# For example:
event = mud.Event(mud.Note('C#6', 1.0), time=1.0)   # A quarter note with pitch C#6 offset 1.0
                                                    # from the start of it's span (not piece)

formatter.make_vector(event)
# The first line is from NoteRelativePitch, the second from NoteLength
# torch.FloatTensor([0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.  
#                    0., 0., 0., 0., 1., 0., 0., 0.])

formatter.make_labels(event)
# (1, 5)

# If we want to format the entire corpus produced earlier:
dataset = []
for piece in corpus:
    piece_bars = []
    for bar in piece:
        bar_vectors = []
        bar_labels = []
        for event in bar:
            bar_vectors.append(formatter.make_vector(event))
            bar_labels.append(formatter.make_labels(event))
        piece_bars.append((bar_vectors, bar_labels))
    dataset.append(piece_bars)

# We now have a structure:
# dataset
#   contains pieces
#       which contain (vectors, labels) pairs
#           vectors contain list of vector representations for each event
#           labels contain list of labels for each specified label for each event
```
The final result is a nested container of pieces, each containing bars, each containing time slices (0.5 beats long),
each containing simultaneous events.
Each event has has a vector and set of labels generated according to the pattern specified by the formatter object.

## Features
### Data formatting
Time quantization and time slicing API for finding all events occuring within a particular
time range.
```python
piece = mud.Piece('path/to/piece.musicxml', discard_rests=True)
# Pieces are represented as a number of Spans.
# Spans are generic subsections of a piece of music.
# However, mud.Piece is stored by default with Spans containing each measure of the piece.
# You can retrieve the entire piece as a single Span using `Piece(...).as_span()`, or
# iterate over events using `for event in piece.events()`.

# If we want to take a look at this, we can do:
piece.show()
#   Piece: path/to/piece.musicxml
#       {Span 0} (Time[0.0, resolution=0.125, steps=0] to Time[4.0, resolution=0.125, steps=32]):
#           {Event 0.0} Note [ 'C4', 1.0 ]
#           {Event 0.0} Note [ 'G5', 1.0 ]
#           {Event 2.0} Note [ 'C4', 2.0 ]
#           {Event 2.0} Note [ 'A4', 2.0 ]

# Now, to see all events occuring within time 2.5 to 3.0 (in beats/quarter notes):
ts = piece.as_span().get_slice((2.5, 3.0))  # .as_span() returns the entire Piece expressed
                                            # in a single Span. (.get_slice() is a Span method)
from pprint import pprint
pprint(ts.raw_events())
#   [Event[Note [ 'C4', 2.0 ], time=Time[2.0, resolution=0.125]],
#    Event[Note [ 'A4', 2.0 ], time=Time[2.0, resolution=0.125]]]

# If we want to iterate through sliced versions of the events, we can use ts.sliced_events(),
# which will also mark whether the event extends before or beyond the slice:
pprint(list(ts.sliced_events()))
#   [SlicedEvent[Note [ 'C4', 0.5 ], time=Time[2.5, resolution=0.125, steps=20], start=False, end=False],
#    SlicedEvent[Note [ 'A4', 0.5 ], time=Time[2.5, resolution=0.125, steps=20], start=False, end=False]]
# We are presented with two events, the C4 and A4, starting at offset 2.5 with length 0.5.
# These sliced events are marked with start and end as False, meaning they are neither the start nor the
# end of the event before it was sliced.

# It's also useful to check whether any of the contained events are smaller than the slice.
# This is referred to as an 'atomic slice' by `mud`.
if not ts.is_atomic_slice(): raise "this won't be raised"
```

Extensible input/label generation for musical events (currently notes and rests).
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
