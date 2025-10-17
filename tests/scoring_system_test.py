import unittest
from text_processing import TextProcessor


class TestScoringSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scorer = TextProcessor("datas/AFINN-en-165.txt")

    def test_score_sentence_positive(self):
        sentence = "I love this movie, it was amazing and fantastic!"
        score = self.scorer.score_sentence(sentence)
        self.assertGreater(score, 0)

    def test_score_sentence_negative(self):
        sentence = "I hate this movie, it was terrible and boring."
        score = self.scorer.score_sentence(sentence)
        self.assertLess(score, 0)

    def test_score_sentence_neutral(self):
        sentence = "The movie was released in 2020."
        score = self.scorer.score_sentence(sentence)
        self.assertEqual(score, 0)

    def test_score_review_average(self):
        review = "I love the story but I hate the ending."
        avg = self.scorer.score_review(review)
        self.assertIsInstance(avg, float)
        self.assertTrue(-2 < avg < 2)

    def test_score_sentence_empty(self):
        sentence = ""
        score = self.scorer.score_sentence(sentence)
        self.assertEqual(score, 0)

    def test_invalid_input_type(self):
        result = self.scorer.score_sentence(None)
        self.assertEqual(result, 0)

    def test_afinn_dictionary_loaded(self):
        self.assertTrue(hasattr(self.scorer, "afinn"))
        self.assertIsInstance(self.scorer.afinn, dict)
        self.assertGreater(len(self.scorer.afinn), 0)
        
# to test: python -m unittest tests/scoring_system_test.py   