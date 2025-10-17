import os
import tempfile
import unittest
import pandas as pd
from movie_comparison import compare_movies


class TestMovieComparison(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create temporary files for testing movie comparison."""
        # Create a small sentiment dictionary file
        cls.temp_dict = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8")
        cls.temp_dict.write("good\t3\nbad\t-2\namazing\t4\nterrible\t-3\n")
        cls.temp_dict.close()

        # Create a sample reviews CSV
        cls.temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8")
        sample_data = pd.DataFrame({
            "movie_title": ["Movie A", "Movie A", "Movie B", "Movie B", "Movie C"],
            "review_content": [
                "This movie is good and amazing",
                "Really bad start but amazing ending",
                "Terrible acting and bad story",
                "Amazing visuals and good soundtrack",
                "Neutral movie overall"
            ]
        })
        sample_data.to_csv(cls.temp_csv.name, index=False)
        cls.temp_csv.close()

    @classmethod
    def tearDownClass(cls):
        """Remove temporary files."""
        os.remove(cls.temp_csv.name)
        os.remove(cls.temp_dict.name)

    def test_compare_two_movies(self):
        """Should return stats for both movies with average sentiments."""
        result = compare_movies(
            self.temp_csv.name,
            "Movie A",
            "Movie B",
            dict_path=self.temp_dict.name
        )

        self.assertIsInstance(result, dict)
        self.assertIn("Movie A", result)
        self.assertIn("Movie B", result)

        # Check that average sentiment and review count exist
        self.assertIn("average_sentiment", result["Movie A"])
        self.assertIn("review_count", result["Movie B"])

        # Average sentiment of Movie A should be higher than Movie B
        self.assertGreater(result["Movie A"]["average_sentiment"], result["Movie B"]["average_sentiment"])

    def test_missing_movies(self):
        """Should return an error message when movies are not found."""
        result = compare_movies(
            self.temp_csv.name,
            "Unknown 1",
            "Unknown 2",
            dict_path=self.temp_dict.name
        )
        self.assertIn("error", result)

    def test_partial_movie_missing(self):
        """One movie exists, the other does not."""
        result = compare_movies(
            self.temp_csv.name,
            "Movie A",
            "Unknown 2",
            dict_path=self.temp_dict.name
        )

        self.assertIn("Movie A", result)
        self.assertIn("Unknown 2", result)
        self.assertIn("error", result["Unknown 2"])


if __name__ == "__main__":
    unittest.main()


# to test: python -m unittest tests/movie_comparison_test.py 