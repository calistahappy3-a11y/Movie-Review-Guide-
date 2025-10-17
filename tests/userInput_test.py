import unittest
import os
import pandas as pd
from user_input import check_review_exists, save_to_csv, get_all_movie_names, suggest_movie_name

class TestUserInput(unittest.TestCase):

    def setUp(self):
        """Run before each test — create a temporary CSV file."""
        self.test_csv = "test_reviews.csv"
        test_data = pd.DataFrame({
            "movie_title": ["Inception", "Interstellar", "The Dark Knight"],
            "review_content": ["Amazing visuals!", "Great story.", "Masterpiece"]
        })
        test_data.to_csv(self.test_csv, index=False)

    def tearDown(self):
        """Run after each test — clean up."""
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

    def test_check_review_exists_true(self):
        result = check_review_exists("Inception", "Amazing visuals!", csv_file=self.test_csv)
        self.assertTrue(result)

    def test_check_review_exists_false(self):
        result = check_review_exists("Inception", "Bad movie", csv_file=self.test_csv)
        self.assertFalse(result)

    def test_save_to_csv_adds_new_entry(self):
        save_to_csv("Tenet", "Mind-blowing!", csv_file=self.test_csv)
        df = pd.read_csv(self.test_csv)
        self.assertIn("Tenet", df["movie_title"].values)
        self.assertIn("Mind-blowing!", df["review_content"].values)

    def test_get_all_movie_names(self):
        movie_names = get_all_movie_names(self.test_csv)
        expected = ["Inception", "Interstellar", "The Dark Knight"]
        self.assertCountEqual(movie_names, expected)

    def test_suggest_movie_name(self):
        suggested = suggest_movie_name("Interstelar", csv_file=self.test_csv)  # intentionally misspelled
        self.assertEqual(suggested, "Interstellar")

    def test_suggest_movie_name_no_match(self):
        suggested = suggest_movie_name("CompletelyDifferent", csv_file=self.test_csv)
        self.assertIsNone(suggested)

if __name__ == '__main__':
    unittest.main()


# to test: python -m unittest tests/userInput_test.py