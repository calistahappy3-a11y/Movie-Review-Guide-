import pandas as pd


def search_reviews(filepath, keyword, title_column="movie_title", text_column="review_content"):
    """
    Search reviews by keyword in movie title or review text.
    Returns a DataFrame of matches.
    """
    df = pd.read_csv(filepath, low_memory=False)

    # drop rows missing title or review
    df = df.dropna(subset=[title_column, text_column])

    keyword = (keyword or "").lower()
    mask = (
        df[title_column].astype(str).str.lower().str.contains(keyword, na=False) |
        df[text_column].astype(str).str.lower().str.contains(keyword, na=False)
    )
    return df[mask]


if __name__ == "__main__":
    # Example usage
    filepath = "datas/cleaned_reviews.csv"
    keyword = input("Enter movie name or keyword to search: ")

    matches = search_reviews(filepath, keyword)

    if matches.empty:
        print("No results found.")
    else:
        print(f"Found {len(matches)} results:\n")
        for i, row in matches.head(10).iterrows():  # show first 10 matches
            print(f"Movie: {row['movie_title']}")
            print(f"Review: {row['review_content'][:100]}...\n")
