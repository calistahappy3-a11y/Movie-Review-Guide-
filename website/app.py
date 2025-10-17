from flask import Flask, request, jsonify, render_template
from pathlib import Path
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from search import search_reviews
from user_input import check_review_exists, save_to_csv, suggest_movie_name, get_all_movie_names
from sliding_window import get_sentiment_windows
from view_movies import MovieViewer
from movie_comparison import compare_movies 

app = Flask(__name__, template_folder='templates', static_folder='static')
CSVPATH = Path("../datas/cleaned_reviews.csv")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # goes up one folder
CSV_PATH = os.path.join(BASE_DIR, "datas", "cleaned_reviews.csv")
movie_viewer = MovieViewer(str(CSV_PATH))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sentiment_analysis')
def sentiment_analysis():
    max_idx, min_idx, window_reviews, window_scoring, window_movie_titles = get_sentiment_windows()

    result = {
        'top_sentiment': {
            'average_score': window_scoring[max_idx],
            'reviews': [{'title': t, 'review': r, 'score': window_scoring[max_idx]}
                       for t, r in zip(window_movie_titles[max_idx], window_reviews[max_idx])]
        },
        'worst_sentiment': {
            'average_score': window_scoring[min_idx],
            'reviews': [{'title': t, 'review': r, 'score': window_scoring[min_idx]}
                       for t, r in zip(window_movie_titles[min_idx], window_reviews[min_idx])]
        }
    }
    return jsonify(result)

@app.route('/search', methods=['GET'])
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({"error": "No query provided"}), 400
    try:
        df = search_reviews(str(CSVPATH), q)
    except FileNotFoundError:
        return jsonify({"error": "CSV file not found"}), 500
    records = df.head(20)[['movie_title', 'review_content']].fillna('').to_dict(orient='records')
    return jsonify(records)

@app.route('/add_review', methods=['POST'])
def add_review():
    data = request.get_json()
    movie_name = data.get('movie_name', '').strip()
    review = data.get('review', '').strip()
    confirm = data.get('confirm')

    if not movie_name or not review:
        return jsonify({"error": "Missing movie_name or review"}), 400

    movie_list = get_all_movie_names(str(CSVPATH))

    movie_exists = any(m.lower() == movie_name.lower() for m in movie_list)

    if not movie_exists:
        suggested = suggest_movie_name(movie_name)
        if suggested and suggested.lower() != movie_name.lower():
            if confirm != 'yes':
                return jsonify({
                    "message": f"Did You Mean {suggested}?",
                    "suggestion": suggested
                }), 206
            else:
                movie_name = suggested
                movie_exists = True

    if not movie_exists:
        return jsonify({"error": "Movie name not recognized. Please correct it."}), 400

    if check_review_exists(movie_name, review):
        return jsonify({"message": "Review already exists"}), 409

    save_to_csv(movie_name, review)

    return jsonify({"message": "Review added successfully"})


@app.route('/all_movies')
def all_movies():
    try:
        df = pd.read_csv(CSV_PATH)
        df = df.drop_duplicates(subset=['movie_title'])
        df = df.where(pd.notnull(df), None)
        movies = df[['movie_title', 'genres']].to_dict(orient='records')
        return jsonify({'movies': movies})
    except Exception as e:
        print("Error in /all_movies:", e)
        return jsonify({'error': str(e)}), 500
    
# @app.route('/compare_movies')
# def compare_movies_route():
#     movie1 = request.args.get('movie1')
#     movie2 = request.args.get('movie2')

#     if not movie1 or not movie2:
#         return jsonify({"error": "Please provide both movie names."}), 400

#     # Use the parent-level movie_comparison.py
#     result = compare_movies(
#         os.path.join(os.path.dirname(__file__), 'data', 'reviews.csv'),
#         movie1,
#         movie2,
#         dict_path=os.path.join(os.path.dirname(__file__), 'data', 'sentiment_dictionary.txt')
#     )
#     return jsonify(result)

@app.route('/compare_movies')
def compare_movies_route():
    movie1 = request.args.get('movie1')
    movie2 = request.args.get('movie2')

    if not movie1 or not movie2:
        return jsonify({"error": "Please provide both movie names."}), 400

    try:
        # Debug prints to Flask console
        print("=== /compare_movies called ===")
        print("movie1:", movie1, "movie2:", movie2)
        print("CSV_PATH:", CSV_PATH)
        print("CSV exists?:", os.path.exists(CSV_PATH))
        dict_path = os.path.join(BASE_DIR, "datas", "AFINN-en-165.txt")
        print("dict_path:", dict_path, "exists?:", os.path.exists(dict_path))

        result = compare_movies(
            CSV_PATH,
            movie1,
            movie2,
            dict_path=dict_path
        )

        # Print a short summary of result to console for debugging
        if isinstance(result, dict):
            print("compare_movies returned keys:", list(result.keys())[:10])
        else:
            print("compare_movies returned non-dict:", type(result))

        return jsonify(result)

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print("Exception in /compare_movies:\n", tb)
        # For local debugging, return the trace too (remove in production)
        return jsonify({"error": str(e), "traceback": tb}), 500


if __name__ == "__main__":
    app.run(debug=True)
