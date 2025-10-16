import pandas as pd


class MovieViewer:
    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)

    def get_all_movies(self):
        """Return list of all unique movies with their genres"""
        return self.df[["movie_title", "genres"]].drop_duplicates().to_dict(orient="records")

    def get_movies_by_genre(self):
        """Group movies by genre and return dict {genre: [movies]}"""
        grouped = {}
        for idx, row in self.df.iterrows():
            movie = row["movie_title"]
            genres = row["genres"].split(",")  # split multiple genres
            for genre in genres:
                genre = genre.strip()  # remove extra spaces
                if genre not in grouped:
                    grouped[genre] = []
                if movie not in grouped[genre]:
                    grouped[genre].append(movie)
        return grouped


# Quick test
if __name__ == "__main__":
    viewer = MovieViewer("datas/cleaned_reviews.csv")

    print("All Movies:")
    print(viewer.get_all_movies())

    print("\nMovies Grouped by Genre:")
    grouped = viewer.get_movies_by_genre()
    for genre, movies in grouped.items():
        print(f"{genre}: {movies}")
