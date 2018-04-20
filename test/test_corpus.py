import unittest
import mud
import os

class TestCorpus(unittest.TestCase):
    def test(self):
        corpus = mud.Corpus(patterns=('test/test-files/canon_in_d.mxl',
                                      'test/test-files/piece.musicxml'))
        self.assertEqual(corpus.size(), 2)
        expected_bars = (27, 1)
        for piece, num_expected_bars in zip(corpus.pieces(), expected_bars):
            self.assertEqual(piece.num_bars(), num_expected_bars)

    def test_filter(self):
        filter_is_short = lambda p: p.num_bars() <= 16
        corpus = mud.Corpus(patterns=('test/test-files/canon_in_d.mxl',
                                      'test/test-files/piece.musicxml'),
                            filters=(filter_is_short,))
        self.assertEqual(corpus.size(), 1)
        for p in corpus.pieces():
            self.assertEqual(p.num_bars(), 1)

    def test_io(self):
        new_corpus_path = 'test/test-temp/corpus'
        if os.path.exists(new_corpus_path):
            os.remove(new_corpus_path)
        files = ('test/test-files/canon_in_d.mxl',
                 'test/test-files/piece.musicxml')
        corpus = mud.Corpus(patterns=files)
        corpus.save(new_corpus_path)
        self.assertTrue(os.path.exists(new_corpus_path))

        new_corpus = mud.Corpus(from_file=new_corpus_path)
        self.assertEqual(corpus.size(), new_corpus.size())
        for piece, expected_name in zip(new_corpus.pieces(), files):
            self.assertEqual(piece.name, expected_name)

        os.remove(new_corpus_path)

class TestDataCorpus(unittest.TestCase):
    def test(self):
        from mud.fmt import label, feature
        files = ('test/test-files/canon_in_d.mxl',
                 'test/test-files/piece.musicxml')
        corpus = mud.Corpus(patterns=files)
        formatter = mud.fmt.EventDataBuilder(
            features=(feature.IsNote(),
                      feature.IsRest(),
                      feature.NoteRelativePitch()),
            labels  =(label.IsNote(),
                      label.RelativePitchLabels()))
        resolution = 1.0 / 4.0
        data_corpus = corpus.format_data(formatter, resolution)
        
        # First piece
        self.assertEqual(len(data_corpus.data[0].bars), 27)
        self.assertEqual(len(data_corpus.data[1].bars), 1)