import mud
import code
from mud.fmt import feature, label
import music21 as m21
from pprint import pprint

res = 0.25
octave_range = (4, 8)
#piece_name = 'Legend_of_Zelda_Breath_of_the_Wild_-_Miphas_Theme_Piano_Cover'
piece_name = 'Avengers_Theme_Duet'
piece_path = f'../neuralcomposer/data/train/{piece_name}.mxl'

piece = mud.Piece(piece_path)
assert mud.piece_filter.AtomicSlicable(res)(piece)
piece.discard_rests()
formatter = mud.fmt.EventDataBuilder(
        features=(feature.NoteRelativePitch(),
                  #feature.NoteOctave(octave_range, saturate=True),
                  feature.ContinuesNextEvent()),
        labels  =(label.RelativePitchLabels(),
                  #label.OctaveLabels(octave_range, saturate=True),
                  label.ContinuesNextEventLabel()),
        library ='numpy',
    )
pdata = mud.fmt.PieceData(piece, formatter, slice_resolution=res)
mp = m21.converter.parse(piece_path)

print('* To interact:')
print('    piece variable: \'piece\'')
print('    piece data variable: \'pdata\'')
print('    music21 piece variable: \'mp\'')
code.interact(local=locals())
# pprint([[[(event.vec, event.labels) for event in ts.events] for ts in bar.timeslices] for bar in pdata.bars], indent=2)