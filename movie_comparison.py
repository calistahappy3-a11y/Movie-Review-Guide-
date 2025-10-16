from pathlib import Path
import pandas as pd
from text_processing import TextProcessor
from scoring_system import process_reviews_df

def compare_movies(filepath, movie1, movie2, dict_path="datas/AFINN-en-165.txt"):
    """
    Robust compare function:
    - Checks file existence
    - Normalizes title column and input to lowercase
    - Returns helpful debug info in errors
    """
    filepath = str(filepath)
    debug = {"filepath": filepath}

    # 1) file exists?
    p = Path(filepath)
    if not p.exists():
        return {"error": f"Data file not found: {filepath}", "debug": debug}

    # 2) load reviews using your TextProcessor (keeps your existing loader)
    processor = TextProcessor(dict_path)
    df_reviews = processor.load_reviews(filepath, return_df=True)

    if df_reviews is None:
        return {"error": "processor.load_reviews returned None", "debug": debug}
    if df_reviews.empty:
        return {"error": "No reviews loaded from file.", "debug": {"columns": df_reviews.columns.tolist()}}

    # 3) find movie title column flexibly
    title_col = None
    for c in df_reviews.columns:
        if c.strip().lower() in ("movie title", "movie_title", "title", "movie"):
            title_col = c
            break
    if title_col is None:
        for c in df_reviews.columns:
            if "movie" in c.lower() or "title" in c.lower():
                title_col = c
                break
    if title_col is None:
        return {
            "error": "No movie-title column found in dataset.",
            "debug": {"columns": df_reviews.columns.tolist()}
        }

    # 4) normalize titles for case-insensitive matching
    df_reviews['movie_title_norm'] = df_reviews[title_col].astype(str).str.strip().str.lower()

    m1 = movie1.strip().lower()
    m2 = movie2.strip().lower()

    # show a small sample of unique titles for debugging
    unique_titles = sorted(df_reviews['movie_title_norm'].unique().tolist())[:200]

    # 5) filter case-insensitively
    df_filtered = df_reviews[df_reviews['movie_title_norm'].isin([m1, m2])]
    if df_filtered.empty:
        return {
            "error": "No reviews found for the given movies.",
            "debug": {
                "m1": m1,
                "m2": m2,
                "available_titles_sample": unique_titles[:50],
                "total_reviews_in_file": int(len(df_reviews))
            }
        }

    # 6) process sentiment on the filtered df
    df_sentiment = process_reviews_df(df_filtered.copy(), processor)
    if df_sentiment is None or df_sentiment.empty:
        return {"error": "Sentiment processing returned empty result.", "debug": {"filtered_count": int(len(df_filtered))}}

    # Ensure normalized title column exists in df_sentiment
    if 'movie_title_norm' not in df_sentiment.columns:
        if title_col in df_sentiment.columns:
            df_sentiment['movie_title_norm'] = df_sentiment[title_col].astype(str).str.strip().str.lower()
        elif 'Movie Title' in df_sentiment.columns:
            df_sentiment['movie_title_norm'] = df_sentiment['Movie Title'].astype(str).str.strip().str.lower()
        elif 'movie_title' in df_sentiment.columns:
            df_sentiment['movie_title_norm'] = df_sentiment['movie_title'].astype(str).str.strip().str.lower()
        else:
            # fallback: reuse df_filtered column if present
            if 'movie_title_norm' in df_filtered.columns:
                df_sentiment['movie_title_norm'] = df_filtered['movie_title_norm'].values
            else:
                return {
                    "error": "Processed sentiment DataFrame lacks a movie-title column.",
                    "debug": {"df_sentiment_columns": df_sentiment.columns.tolist()}
                }

    # 7) find a numeric score column (prefer 'Average Score')
    score_col = None
    for c in df_sentiment.columns:
        if 'average' in c.lower() and 'score' in c.lower():
            score_col = c
            break
    if score_col is None:
        numeric_cols = [c for c in df_sentiment.columns if pd.api.types.is_numeric_dtype(df_sentiment[c])]
        score_like = [c for c in numeric_cols if 'score' in c.lower()]
        score_col = score_like[0] if score_like else (numeric_cols[0] if numeric_cols else None)

    # 8) compute stats
    stats = {}
    for orig_name in [movie1, movie2]:
        name_norm = orig_name.strip().lower()
        df_m = df_sentiment[df_sentiment['movie_title_norm'] == name_norm]

        if df_m.empty:
            stats[orig_name] = {"error": "No reviews for this movie after sentiment processing."}
            continue

        average_sentiment = float(df_m[score_col].mean()) if score_col is not None else None

        if score_col is not None:
            most_pos_row = df_m.loc[df_m[score_col].idxmax()].to_dict()
            most_neg_row = df_m.loc[df_m[score_col].idxmin()].to_dict()
        else:
            most_pos_row = df_m.iloc[0].to_dict()
            most_neg_row = df_m.iloc[0].to_dict()

        # convert numpy scalars to python types for JSON
        try:
            import numpy as _np
            for d in (most_pos_row, most_neg_row):
                for k, v in list(d.items()):
                    if isinstance(v, _np.generic):
                        d[k] = v.item()
        except Exception:
            pass

        stats[orig_name] = {
            "average_sentiment": average_sentiment,
            "review_count": int(len(df_m)),
            "most_positive": most_pos_row,
            "most_negative": most_neg_row,
        }

    return stats



if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python movie_comparison.py <movie1> <movie2>")
        sys.exit(1)

    movie1 = sys.argv[1]
    movie2 = sys.argv[2]

    filepath = "datas/cleaned_reviews.csv"
    result = compare_movies(filepath, movie1, movie2)
    print(result)
