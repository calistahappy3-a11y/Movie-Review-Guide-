import unittest
from sliding_window import sliding_window_analysis

class TestSlidingWindow(unittest.TestCase):

    def test_basic_case(self):
        scores = [1, 0, 1, 2, 5, 6, 7, 8]  # sentiment scores
        reviews = ["r1","r2","r3","r4","r5","r6","r7","r8"]
        movies = ["m1","m2","m3","m4","m5","m6","m7","m8"]

        max_idx, min_idx, window_reviews, window_scoring, window_movie_titles = sliding_window_analysis(
            scores, reviews, movies, window_size=3
        )

        # Check that window_scoring has correct length
        self.assertEqual(len(window_scoring), len(scores) - 3 + 1)

        # Check max and min
        self.assertEqual(max_idx, window_scoring.index(max(window_scoring)))
        self.assertEqual(min_idx, window_scoring.index(min(window_scoring)))

    def test_empty_array(self):
        scores = []
        reviews = []
        movies = []

        max_idx, min_idx, window_reviews, window_scoring, window_movie_titles = sliding_window_analysis(
            scores, reviews, movies, window_size=3
        )

        self.assertEqual(window_scoring, [])
        self.assertEqual(window_reviews, [])
        self.assertEqual(window_movie_titles, [])
        self.assertIsNone(max_idx)
        self.assertIsNone(min_idx)

if __name__ == '__main__':
    unittest.main()


# to test: python -m unittest tests/slidingWindow_test.py