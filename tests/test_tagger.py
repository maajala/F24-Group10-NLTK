import unittest
from src.tagger.simple_unigram_trainer import UnigramTrainer
from src.tagger.simple_unigram_tagger import UnigramTagger

class TestUnigramTagger(unittest.TestCase):
    def test_tagger(self):
        corpus = [[('I', 'PRP'), ('love', 'VBP'), ('Python', 'NN')]]
        trainer = UnigramTrainer(corpus)
        trainer.train()

        tagger = UnigramTagger(trainer.get_model())
        text = ['I', 'love', 'Python']
        tagged = tagger.tag(text)

        self.assertEqual(tagged, [('I', 'PRP'), ('love', 'VBP'), ('Python', 'NN')])

if __name__ == '__main__':
    unittest.main()

