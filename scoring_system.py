import os
import pandas as pd
import json
from text_processing import TextProcessor
import nltk

# Download the NLTK 'punkt' tokeniser quietly (used for sentence splitting)
nltk.download("punkt", quiet=True)


def process_reviews_df(
    df_reviews,
    processor,
    review_col="review_content",
    movie_title_col="movie_title",
    limit=None
):
    """
    Process a DataFrame of movie reviews and calculate sentiment scores.

    Parameters:
        df_reviews (DataFrame): The input DataFrame containing movie reviews.
        processor (TextProcessor): The text processor object used for cleaning and scoring text.
        review_col (str): Column name containing the review text.
        movie_title_col (str): Column name containing the movie title.
        limit (int, optional): Maximum number of reviews to process.

    Returns:
        DataFrame: A new DataFrame containing each review’s average sentiment score,
                   most positive and most negative sentences, and their scores.
    """

    # Drop any rows missing required columns
    df_reviews = df_reviews.dropna(subset=[review_col, movie_title_col])

    records = []
    for idx, row in df_reviews.iterrows():
        if limit is not None and idx >= limit:
            break  # Stop processing once limit is reached

        movie = row[movie_title_col]
        text = row[review_col]

        # Skip invalid (non-string) reviews
        if not isinstance(text, str):
            continue

        # Clean and score the review
        cleaned_text = processor.preprocess_text(text)
        avg_score = processor.score_review(cleaned_text)

        # Split review into sentences and score each one
        sentences = processor.split_sentences(cleaned_text)
        sentence_scores = [(s, processor.score_sentence(s)) for s in sentences]

        # Identify the most positive and most negative sentences
        most_positive = max(sentence_scores, key=lambda x: x[1]) if sentence_scores else ("", 0)
        most_negative = min(sentence_scores, key=lambda x: x[1]) if sentence_scores else ("", 0)

        # Helper function to format long sentences neatly
        def format_sentence(s, max_len=80):
            if len(s) > max_len:
                return s[:max_len - 3] + "..."
            else:
                return s.ljust(max_len)

        # Append processed data to list
        records.append({
            "Movie Title": movie,
            "Review Text": text,
            "Average Score": avg_score,
            "Most Positive Sentence": format_sentence(most_positive[0]),
            "Most Positive Score": most_positive[1],
            "Most Negative Sentence": format_sentence(most_negative[0]),
            "Most Negative Score": most_negative[1],
        })

    # Return all processed results as a DataFrame
    return pd.DataFrame(records)


def summarize_movies(df_sentiment, top_n=5):
    """
    Summarise movies by their average sentiment score.

    Parameters:
        df_sentiment (DataFrame): DataFrame containing sentiment scores for each review.
        top_n (int): Number of top and bottom movies to return.

    Returns:
        tuple: Two DataFrames (top, bottom) representing the highest- and lowest-scoring movies.
    """

    # Calculate average sentiment score per movie
    movie_avg = df_sentiment.groupby("Movie Title")["Average Score"].mean().reset_index()
    movie_avg["Average Score"] = movie_avg["Average Score"].round(2)

    # Sort movies from highest to lowest score
    movie_avg = movie_avg.sort_values("Average Score", ascending=False)

    # Select top and bottom N movies
    top = movie_avg.head(top_n).reset_index(drop=True)
    bottom = movie_avg.tail(top_n).sort_values("Average Score").reset_index(drop=True)

    return top, bottom


def print_top_bottom_movies(df_sentiment, top_n=5):
    """
    Print the top and bottom movies by average sentiment score.

    Parameters:
        df_sentiment (DataFrame): DataFrame containing sentiment scores for each review.
        top_n (int): Number of movies to display in each category.
    """

    top_movies, worst_movies = summarize_movies(df_sentiment, top_n)
    print("\nTop Movies by Sentiment:")
    print(top_movies.to_string(index=False))
    print("\nWorst Movies by Sentiment:")
    print(worst_movies.to_string(index=False))


def print_extreme_sentences(df_sentiment, processor, top_n=5):
    """
    Print the most positive and most negative sentences across all reviews.

    Parameters:
        df_sentiment (DataFrame): DataFrame containing review text and sentiment scores.
        processor (TextProcessor): TextProcessor object used for scoring sentences.
        top_n (int): Number of extreme sentences to display for each category.
    """

    all_sentences = []

    # Extract and score all sentences from all reviews
    for _, row in df_sentiment.iterrows():
        text = row["Review Text"]
        movie = row["Movie Title"]
        cleaned_text = processor.preprocess_text(text)
        sentences = processor.split_sentences(cleaned_text)
        for s in sentences:
            score = processor.score_sentence(s)
            all_sentences.append((movie, s, score))

    # Sort and print the most positive sentences
    all_sentences_sorted = sorted(all_sentences, key=lambda x: x[2], reverse=True)
    print("\n=== Top 5 Most Positive Sentences ===")
    for i in range(min(top_n, len(all_sentences_sorted))):
        m, s, sc = all_sentences_sorted[i]
        print(f"{i+1}. Movie: {m}")
        print(f"   Score: {sc}")
        print(f"   Sentence: {s}\n")

    # Sort and print the most negative sentences
    all_sentences_sorted_neg = sorted(all_sentences, key=lambda x: x[2])
    print("\n=== Top 5 Most Negative Sentences ===")
    for i in range(min(top_n, len(all_sentences_sorted_neg))):
        m, s, sc = all_sentences_sorted_neg[i]
        print(f"{i+1}. Movie: {m}")
        print(f"   Score: {sc}")
        print(f"   Sentence: {s}\n")


def export_top_worst_movies_to_json(top_df, worst_df, output_file=None):
    """
    Export the top and worst movies to a JSON file for website integration.

    Parameters:
        top_df (DataFrame): DataFrame containing top-rated movies.
        worst_df (DataFrame): DataFrame containing the lowest-rated movies.
        output_file (str, optional): Output file path. Defaults to 'website/static/top_worst_movies.json'.
    """

    # Prepare dictionary data for export
    result = {
        "top_movies": top_df["Movie Title"].tolist(),
        "worst_movies": worst_df["Movie Title"].tolist()
    }

    # Define default output path if not specified
    if output_file is None:
        website_folder = os.path.join(os.path.dirname(__file__), "website", "static")
        os.makedirs(website_folder, exist_ok=True)  # Ensure target folder exists
        output_file = os.path.join(website_folder, "top_worst_movies.json")

    # Write results to JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"Exported top/worst movies JSON to: {output_file}")


if __name__ == "__main__":
    # Initialise the text processor with a sentiment lexicon
    processor = TextProcessor("datas/AFINN-en-165.txt")

    # Load cleaned movie review data
    df_reviews = processor.load_reviews("datas/cleaned_reviews.csv", return_df=True, n=1000)

    # Process reviews and calculate sentiment statistics
    df_sentiment = process_reviews_df(df_reviews, processor, limit=1000)

    # Summarise top and bottom movies by sentiment
    top_movies, worst_movies = summarize_movies(df_sentiment, top_n=5)

    # Export results to JSON for website display
    export_top_worst_movies_to_json(top_movies, worst_movies)

    # Display results in console
    print_top_bottom_movies(df_sentiment, top_n=5)
    print_extreme_sentences(df_sentiment, processor, top_n=5)
