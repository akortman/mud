import mud
import argparse

parser = argparse.ArgumentParser(description='Open a music file and show the Piece representation.')
parser.add_argument('path', type=str, help='the path to the piece to show')
args = parser.parse_args()

p = mud.Piece(args.path)
p.pprint()