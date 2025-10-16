
#from afinn import Afinn


#afdict = Afinn() #creates a placeholder for the afinn dictionary
#looks up sentiment score for the input and calculates the sum
#list_reviews = ["i hate this movie.", "this movie sucks balls", "this movie is so so so good!", "great movie and good actors", "could be better but overall still okay."]
#reviews = [afdict.score(i) for i in list_reviews]

#start of sliding window

#window_size = 3
#window_scoring = [] #stores all the scores into an array
#for x in range(len(reviews)- window_size + 1): #loop through how many windows are there in the list provided
#  window = reviews[x:x+window_size] #slices the list into windows of 3
#  score = sum(window)/window_size #gets the average of the reviews through sentiment analysis
#  window_scoring.append(score) #adds the score into the array

#max_score = window_scoring.index(max(window_scoring)) #finds the index of most positive scoring in the list
#min_score = window_scoring.index(min(window_scoring)) #finds the index of most negative scoring in the list

#positive = list_reviews[max_score:max_score+ window_size]
#negative = list_reviews[min_score:min_score+ window_size]

#print("This is the most postive window" , positive)
#rint("This is the most negative window" , negative)

import pandas as pd
from text_processing import TextProcessor
from scoring_system import process_reviews_df
from pathlib import Path
import nltk

nltk.download("punkt", quiet=True)

# Initialize TextProcessor for the AFINN dictionary
processor = TextProcessor(str(Path(__file__).parent / "datas" / "AFINN-en-165.txt"))

# Load reviews and process them with sentiment scores
df_reviews = processor.load_reviews("datas/cleaned_reviews.csv", return_df=True, n=100)
df_sentiment = process_reviews_df(df_reviews, processor, limit=100)

def sliding_window_analysis(reviews_sentiment, reviews_text, movie_titles, window_size=3):
    # Handle empty inputs
    if not reviews_sentiment or window_size <= 0:
        return None, None, [], [], []
    
    window_scoring = []
    window_reviews = []  # List to store actual review texts for each window
    window_movie_titles = []  # List to store movie names for each window
    for x in range(len(reviews_sentiment) - window_size + 1):
        window = reviews_sentiment[x:x + window_size]  # Get sentiment scores for this window
        reviews_window = reviews_text[x:x + window_size]  # Get actual review texts for this window
        movie_titles_window = movie_titles[x:x + window_size]  # Get movie titles for this window
        score = sum(window) / window_size  # Calculate the average sentiment score for the window
        
        # Store the window sentiment score, corresponding reviews, and movie titles
        window_scoring.append(score)
        window_reviews.append(reviews_window)
        window_movie_titles.append(movie_titles_window)

    max_score_idx = window_scoring.index(max(window_scoring))  # Find the index of the most positive window
    min_score_idx = window_scoring.index(min(window_scoring))  # Find the index of the most negative window

    return max_score_idx, min_score_idx, window_reviews, window_scoring, window_movie_titles


def get_sentiment_windows():
    reviews_sentiment = df_sentiment['Average Score'].tolist()
    reviews_text = df_sentiment['Review Text'].tolist()
    movie_titles = df_sentiment['Movie Title'].tolist()

    max_idx, min_idx, window_reviews, window_scoring, window_movie_titles = sliding_window_analysis(
        reviews_sentiment, reviews_text, movie_titles, window_size=3
    )
    return max_idx, min_idx, window_reviews, window_scoring, window_movie_titles


# Example usage you had for console output (optional)
if __name__ == "__main__":
    max_score_idx, min_score_idx, window_reviews, window_scoring, window_movie_titles = get_sentiment_windows()

    print("\nMost Positive Window Reviews and Score:")
    for i in range(len(window_reviews[max_score_idx])):
        print(f"Movie: {window_movie_titles[max_score_idx][i]} | Review: {window_reviews[max_score_idx][i]}")
    print(f"Average Sentiment Score: {window_scoring[max_score_idx]:.2f}\n")

    print("\nMost Negative Window Reviews and Score:")
    for i in range(len(window_reviews[min_score_idx])):
        print(f"Movie: {window_movie_titles[min_score_idx][i]} | Review: {window_reviews[min_score_idx][i]}")
    print(f"Average Sentiment Score: {window_scoring[min_score_idx]:.2f}\n")