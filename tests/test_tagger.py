import unittest
from tagger.simple_unigram_tagger import UnigramTagger  # Correct import

class TestUnigramTagger(unittest.TestCase):

    def setUp(self):
        # Update the dummy model with the correct tags for the test
        self.dummy_model = {
            'The': 'DT',  # Determiner
            'quick': 'JJ',  # Adjective
            'brown': 'JJ',  # Adjective
            'fox': 'NN',  # Noun
            'I': 'PRP',  # Pronoun
            'saw': 'VBD',  # Verb, past tense
            'a': 'DT',  # Determiner
            'beautiful': 'JJ',  # Adjective
            'bird': 'NN'  # Noun
        }

    def test_empty_input(self):
        # Test that empty string results in an empty list or no tags
        text = []
        tagger = UnigramTagger(self.dummy_model)  # Create an instance with the dummy model
        tagged = tagger.tag_text(text)  # Call tag_text method on the instance
        self.assertEqual(tagged, [])  # Should return an empty list

    def test_correctness_of_tagging(self):
        # Test case with predefined text and expected tagging
        text = ["The", "quick", "brown", "fox"]
        expected_output = [("The", "DT"), ("quick", "JJ"), ("brown", "JJ"), ("fox", "NN")]

        tagger = UnigramTagger(self.dummy_model)  # Create an instance with the dummy model
        tagged = tagger.tag_text(text)  # Call tag_text method on the instance

        self.assertEqual(tagged, expected_output)  # Check if tagging is correct

    def test_mixed_sentence_tagging(self):
        # Test case with mixed sentence
        text = ["I", "saw", "a", "beautiful", "bird"]
        expected_output = [("I", "PRP"), ("saw", "VBD"), ("a", "DT"), ("beautiful", "JJ"), ("bird", "NN")]

        tagger = UnigramTagger(self.dummy_model)  # Create an instance with the dummy model
        tagged = tagger.tag_text(text)  # Call tag_text method on the instance

        self.assertEqual(tagged, expected_output)  # Check if tagging is correct

if __name__ == '__main__':
    unittest.main()

