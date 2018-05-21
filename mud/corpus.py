from glob import iglob
import random
import pickle
import music21 as mu

from .piece import Piece
from .fmt.piece_data import PieceData

class AbstractCorpus(object):
    def __init__(self):
        raise NotImplementedError

    def save(self, fname):   
        with open(fname, 'wb+') as f:
            pickle.dump(self.__dict__,
                        f,
                        pickle.HIGHEST_PROTOCOL)

    def load(self, fname):
        with open(fname, 'rb') as f:
            self.__dict__ = pickle.load(f)

class Corpus(AbstractCorpus):
    def __init__(self, patterns=tuple(), filters=tuple(), from_file=None, discard_rests=False, max_len=None, ignore_load_errors=False, verbose=False):
        '''
        Load a corpus of pieces.
        patterns: an iterable of patterns (ie '*.musicxml') to load into the corpus.
        '''
        self._pieces = []
        self._num_rejected = 0

        if from_file is not None:
            if len(patterns) > 1:
                raise ValueError('Should not provide patterns if loading from file')
            self.load(from_file)
        else:
            def load(self_):
                for pattern in patterns:
                    for fname in iglob(pattern):
                        try:
                            self_.load_piece(fname, filters)
                        except (mu.exceptions21.StreamException, mu.musicxml.xmlToM21.MusicXMLImportException):
                            if verbose: print(f'    Failed to load file {fname}: ', end='')
                            if ignore_load_errors:
                                if verbose: print('continuing')
                                continue
                            if verbose: print('failing (use `ignore_load_errors=True` in corpus to prevent)')
                            raise
                        if verbose: print(f'    loaded {fname}')
                        if max_len is not None and self_.size() >= max_len:
                            return
            load(self)
            
        if discard_rests:
            self.discard_rests()

    def size(self):
        return len(self._pieces)

    @property
    def pieces(self):
        return self._pieces

    @property
    def num_rejected(self):
        return self._num_rejected

    def passes_filters(self, piece, filters):
        for f in filters:
            if not f(piece):
                self._num_rejected += 1
                return False
        return True

    def load_piece(self, piece, filters=tuple()):
        p = Piece(piece)
        if self.passes_filters(p, filters):
            p = self._pieces.append(p)

    def format_data(self, formatter, slice_resolution, discard_rests=False):
        return DataCorpus(self, formatter, slice_resolution, discard_rests)

    def filter(self, *filters):
        '''
        Filter out pieces that do not adhere to a set of filters.
        see: piece_filter.py
        '''
        len_old = len(self._pieces)
        for f in filters:
            self._pieces = [p for p in self._pieces if f(p)]
        self._num_rejected += len_old - len(self._pieces)

    def discard_rests(self):
        for piece in self._pieces:
            piece.discard_rests()

class DataCorpus(AbstractCorpus):
    def __init__(self, corpus, formatter, slice_resolution, discard_rests=False):
        self._data = [PieceData(p, formatter, slice_resolution, discard_rests)
                      for p in corpus.pieces]

    def size(self):
        return len(self._data)

    @property
    def data(self):
        return self._data

    def __iter__(self):
        return self._data.__iter__()
    
    def __len__(self):
        return len(self._data)


