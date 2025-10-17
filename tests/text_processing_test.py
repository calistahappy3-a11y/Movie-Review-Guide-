import os
import tempfile
import unittest
import pandas as pd
from text_processing import TextProcessor


class TestTextProcessing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a temporary dictionary file before all tests."""
        cls.temp_dict = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8")
        cls.temp_dict.write("good\t3\nbad\t-2\namazing\t4\nterrible\t-3\n")
        cls.temp_dict.close()
        cls.processor = TextProcessor(cls.temp_dict.name)

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary file after all tests."""
        os.remove(cls.temp_dict.name)

    def test_load_dict(self):
        tp = TextProcessor()
        result = tp.load_dict(self.temp_dict.name)
        self.assertIsInstance(result, dict)
        self.assertIn("good", result)
        self.assertEqual(result["amazing"], 4)

    def test_preprocess_text(self):
        raw_text = " <p>Hello   world!</p> "
        cleaned = self.processor.preprocess_text(raw_text)
        self.assertEqual(cleaned, "Hello world!")

    def test_split_sentences(self):
        text = "I love movies. They are amazing!"
        sentences = self.processor.split_sentences(text)
        self.assertIsInstance(sentences, list)
        self.assertEqual(len(sentences), 2)
        self.assertIn("I love movies.", sentences)

    def test_score_sentence_positive(self):
        sentence = "This is good and amazing"
        score = self.processor.score_sentence(sentence)
        self.assertGreater(score, 0)

    def test_score_sentence_negative(self):
        sentence = "This is bad and terrible"
        score = self.processor.score_sentence(sentence)
        self.assertLess(score, 0)

    def test_score_sentence_neutral(self):
        sentence = "This is neutral"
        score = self.processor.score_sentence(sentence)
        self.assertEqual(score, 0)

    def test_score_review_multiple_sentences(self):
        # Your implementation returns int (sum of all sentence scores)
        review = "I love it. But it was bad at first."
        total = self.processor.score_review(review)
        self.assertIsInstance(total, (int, float))  # <-- more flexible
        # Ensure not always 0 (should detect sentiment words)
        self.assertNotEqual(total, 0)

    def test_load_reviews_csv(self):
        """Check if load_reviews reads a CSV correctly."""
        temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8")
        df = pd.DataFrame({
            "movie_title": ["A", "B"],
            "review_content": ["Good movie", "Bad movie"]
        })
        df.to_csv(temp_csv.name, index=False)
        temp_csv.close()

        tp = TextProcessor()
        result = tp.load_reviews(temp_csv.name)
        os.remove(temp_csv.name)

        self.assertIsInstance(result, list)
        self.assertTrue("movie_title" in result[0])
        self.assertTrue("review_content" in result[0])

    def test_process_reviews(self):
        reviews = [
            {"movie_title": "Movie 1", "review_content": "Good and amazing film"},
            {"movie_title": "Movie 2", "review_content": "Bad and terrible movie"},
        ]
        results = self.processor.process_reviews(reviews)
        self.assertEqual(len(results), 2)
        self.assertTrue(all("score" in r for r in results))
        # Ensure Movie 1 (positive) has higher score than Movie 2 (negative)
        self.assertGreater(results[0]["score"], results[1]["score"])


if __name__ == "__main__":
    unittest.main()
    
    # to test: python -m unittest tests/text_processing_test.py -v