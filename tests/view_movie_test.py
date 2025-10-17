import os
import tempfile
import unittest
import pandas as pd
from view_movies import MovieViewer


class TestMovieViewer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a temporary CSV file with sample movie data."""
        cls.temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8")

        # Create small sample dataset
        sample_data = pd.DataFrame({
            "movie_title": ["Inception", "Titanic", "Avatar", "The Dark Knight", "Inception"],
            "genres": ["Action,Sci-Fi", "Romance,Drama", "Sci-Fi,Adventure", "Action,Drama", "Action,Sci-Fi"]
        })
        sample_data.to_csv(cls.temp_csv.name, index=False)
        cls.temp_csv.close()

        cls.viewer = MovieViewer(cls.temp_csv.name)

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary CSV file."""
        os.remove(cls.temp_csv.name)

    def test_get_all_movies(self):
        """Check if get_all_movies returns correct unique movies."""
        result = self.viewer.get_all_movies()

        self.assertIsInstance(result, list)
        self.assertTrue(all("movie_title" in movie for movie in result))
        self.assertTrue(all("genres" in movie for movie in result))
        # There should be 4 unique movies (Inception duplicates removed)
        self.assertEqual(len(result), 4)

    def test_get_movies_by_genre(self):
        """Check if movies are grouped correctly by genre."""
        grouped = self.viewer.get_movies_by_genre()

        self.assertIsInstance(grouped, dict)
        self.assertIn("Action", grouped)
        self.assertIn("Drama", grouped)
        self.assertIn("Sci-Fi", grouped)

        # Inception should appear under Action and Sci-Fi
        self.assertIn("Inception", grouped["Action"])
        self.assertIn("Inception", grouped["Sci-Fi"])

        # Titanic should be under Romance and Drama
        self.assertIn("Titanic", grouped["Romance"])
        self.assertIn("Titanic", grouped["Drama"])

    def test_no_duplicate_movies_in_genre(self):
        """Ensure no genre list contains duplicates."""
        grouped = self.viewer.get_movies_by_genre()
        for genre, movies in grouped.items():
            self.assertEqual(len(movies), len(set(movies)), f"Duplicates found in {genre}")


if __name__ == "__main__":
    unittest.main()


# to test: python -m unittest tests/view_movie_test.py -v 