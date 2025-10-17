import os
import tempfile
import unittest
import pandas as pd
from website.search import search_reviews  # adjust if your path differs


class TestSearchReviews(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a temporary CSV file for testing."""
        cls.temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8")

        sample_data = pd.DataFrame({
            "movie_title": ["Inception", "Titanic", "Avatar", "The Dark Knight"],
            "review_content": [
                "Amazing movie with great visuals.",
                "A romantic and emotional masterpiece.",
                "The effects were good but story was weak.",
                "Dark and thrilling superhero film."
            ]
        })
        sample_data.to_csv(cls.temp_csv.name, index=False)
        cls.temp_csv.close()

    @classmethod
    def tearDownClass(cls):
        """Remove temporary file after tests."""
        os.remove(cls.temp_csv.name)

    def test_search_by_title(self):
        """Search keyword that appears in movie title."""
        result = search_reviews(self.temp_csv.name, "Titanic")
        self.assertFalse(result.empty)
        self.assertEqual(result.iloc[0]["movie_title"], "Titanic")

    def test_search_by_review_text(self):
        """Search keyword that appears in review text."""
        result = search_reviews(self.temp_csv.name, "thrilling")
        self.assertFalse(result.empty)
        self.assertIn("Dark Knight", result.iloc[0]["movie_title"])

    def test_case_insensitive_search(self):
        """Search should be case-insensitive."""
        result = search_reviews(self.temp_csv.name, "amAZing")
        self.assertFalse(result.empty)
        self.assertIn("Inception", result["movie_title"].values)

    def test_no_results(self):
        """Search for keyword not found should return empty DataFrame."""
        result = search_reviews(self.temp_csv.name, "aliens")
        self.assertTrue(result.empty)

    def test_empty_keyword_returns_all(self):
        """Empty keyword should return all rows (matches everything)."""
        result = search_reviews(self.temp_csv.name, "")
        self.assertEqual(len(result), 4)


if __name__ == "__main__":
    unittest.main()
