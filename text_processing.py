import re  # for cleaning text
import pandas as pd  # reading CSV files
import nltk
from nltk.tokenize import sent_tokenize

nltk.download("punkt", quiet=True)  # for sentence splitting

"""
Handling text processing and sentiment scoring
"""


class TextProcessor:
    def __init__(self, dict_path=None):
        """
        Initialise processor
        dict_path: path to AFINN sentiment dictionary
        """
        if dict_path:
            self.sentiment_dict = self.load_dict(dict_path)
        else:
            self.sentiment_dict = {}  # empty dict if no path provided
            
        self.afinn = self.sentiment_dict
        
    def load_dict(self, filepath):
        """Load dictionary into Python dict {word: score}"""
        afinn = {}
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                word, score = line.split("\t")
                afinn[word] = int(score)
        return afinn

    def load_reviews(
        self,
        filepath,
        title_column="movie_title",
        text_column="review_content",
        n=None,
        return_df=False
    ):
        """
        Load reviews and movie titles from CSV
        title_column: column containing movie titles
        text_column: column containing review text
        n: number of rows to load for testing
        return_df: if True, return DataFrame instead of list of dicts
        """
        df = pd.read_csv(filepath, low_memory=False)
        df = df.dropna(subset=[text_column])  # remove empty rows
        if n:
            df = df.head(n)  # take only first n rows

        if return_df:
            return df
        return df[[title_column, text_column]].to_dict("records")

    def preprocess_text(self, text):
        """Clean and normalise text"""
        text = re.sub(r"<[^>]+>", " ", text)  # remove HTML tags
        text = text.strip()
        text = re.sub(r"\s+", " ", text)  # normalise whitespace
        return text

    def split_sentences(self, text):
        """Split text into sentences using nltk"""
        return sent_tokenize(text)

    # def score_sentence(self, sentence):
    #     """Score a single sentence using the sentiment dictionary"""
    #     words = re.findall(r"\w+", sentence.lower())  # convert to lowercase
    #     score = 0
    #     for w in words:
    #         if w in self.sentiment_dict:  # check if word has a score
    #             score += self.sentiment_dict[w]
    #     return score
    
    def score_sentence(self, sentence):
        """Score a single sentence using the sentiment dictionary"""
        if not isinstance(sentence, str):
            return 0  # Handle None or non-string input safely

        words = re.findall(r"\w+", sentence.lower())
        score = 0
        for w in words:
            if w in self.sentiment_dict:
                score += self.sentiment_dict[w]
        return score


    # def score_review(self, review):
    #     """Score entire review by summing all sentence scores"""
    #     sentences = self.split_sentences(review)
    #     return sum([self.score_sentence(s) for s in sentences])
    
    def score_review(self, review):
        """Score entire review by averaging all sentence scores"""
        sentences = self.split_sentences(review)
        if not sentences:
            return 0.0
        scores = [self.score_sentence(s) for s in sentences]
        return float(sum(scores)) / len(sentences)


    def process_reviews(self, reviews, title_column="movie_title", text_column="review_content"):
        """
        Process a list of reviews
        Returns list of dicts: {"title": movie_title, "review": text, "score": sentiment_score}
        """
        results = []
        for r in reviews:
            title = r[title_column]
            text = r[text_column]
            cleaned = self.preprocess_text(text)
            score = self.score_review(cleaned)
            results.append({"title": title, "review": text, "score": score})
        return results


"""
Testing 
"""
if __name__ == "__main__":
    processor = TextProcessor("datas/AFINN-en-165.txt")  # path to dictionary
    reviews_df = processor.load_reviews("datas/cleaned_reviews.csv", n=5, return_df=True)

    results = processor.process_reviews(reviews_df.to_dict("records"))
    for r in results:
        print(f"Movie: {r['title']}")
        print(f"Review: {r['review'][:80]}...")  # show first 80 chars
        print(f"Sentiment Score: {r['score']}\n")
