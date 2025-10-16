import os
import pandas as pd
from fuzzywuzzy import process

def check_review_exists(movie_name, review, csv_file="datas/cleaned_reviews.csv"):
    if not os.path.exists(csv_file):
        return False
    df = pd.read_csv(csv_file)
    return ((df['movie_title'] == movie_name) & (df['review_content'] == review)).any()

def save_to_csv(movie_name, review, csv_file="datas/cleaned_reviews.csv"):
    new_data = pd.DataFrame({'movie_title': [movie_name], 'review_content': [review]})

    print(f"Saving CSV to: {os.path.abspath(csv_file)}")

    # dir_path = os.path.dirname(csv_file)
    # if not os.path.exists(dir_path):
    #     os.makedirs(dir_path)
    
# The change was made to handle cases where the CSV file is saved in the current directory.
# Previously, os.makedirs() would fail when given an empty string as the directory path.
# Adding if dir_path ensures that a folder is only created when a valid directory path exists, preventing a FileNotFoundError 

    dir_path = os.path.dirname(csv_file)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)


    if not os.path.exists(csv_file):
        new_data.to_csv(csv_file, mode='w', header=True, index=False)
    else:
        new_data.to_csv(csv_file, mode='a', header=False, index=False)

def get_all_movie_names(csv_file="datas/cleaned_reviews.csv"):
    if not os.path.exists(csv_file):
        return []
    df = pd.read_csv(csv_file)
    movie_names = df['movie_title'].dropna().unique().tolist()
    print(f"Loaded {len(movie_names)} movie names.")
    print(f"Sample movies: {movie_names[:10]}")
    return movie_names

def suggest_movie_name(movie_name, csv_file="datas/cleaned_reviews.csv"):
    movie_list = get_all_movie_names(csv_file)
    if not movie_list:
        return None
    best_match, score = process.extractOne(movie_name, movie_list)
    print(f"suggest_movie_name called: input='{movie_name}', best_match='{best_match}', score={score}")
    if score >= 70:
        return best_match
    else:
        return None
