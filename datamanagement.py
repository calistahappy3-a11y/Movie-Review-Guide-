import pandas as pd
import re

#Loading csv into memory
reviews = pd.read_csv("datas/rottenTomato.csv")
title = pd.read_csv("datas/movieNames.csv")


#merging the reviews and movie name
merged_dataset = reviews.merge(
    title[['rotten_tomatoes_link', 'movie_title', 'genres']],  # only keep needed columns
    on='rotten_tomatoes_link',
    how='left'  # keeps all reviews, even if no matching movie name
)
# print(merged_dataset[['movie_title', 'review_content']].head())


# merged_dataset.info() #data info
# from this info table, i can infer that i can remove all the colomns but leave the movie name and the reviews


#keeping only 2 colomns 
data_table = merged_dataset[['movie_title', 'review_content','genres']]


#check for null value
print("empty:",data_table.isna().sum()) 
#from this, we can see that there are 130 blank movie title and 65806 empty review
#now we remove rows with null values in movie_title or review_content
data_table = data_table.dropna(subset=['movie_title', 'review_content','genres'])
print("updated null:", data_table)

# check for zero value
print ("zero value:",(data_table == 0).sum())
#can see that there are no zero values



# 🔹 Function to check duplicates within movies
def check_duplicates(df):
    duplicates = df[df.duplicated(subset=['movie_title', 'review_content'], keep=False)]
    duplicate_counts = (
        df.groupby(['movie_title', 'review_content'])
        .size()
        .reset_index(name='count')
    )
    duplicate_counts = duplicate_counts[duplicate_counts['count'] > 1]
    return duplicates, duplicate_counts


# Before removing
dups_before, counts_before = check_duplicates(data_table)
print("Before cleanup:")
print(counts_before)


# Remove duplicates (keep last occurrence)
data_table = data_table.drop_duplicates(subset=['movie_title', 'review_content'], keep='last')

# After removing
dups_after, counts_after = check_duplicates(data_table)
print("\nAfter cleanup:")
print(counts_after)


# # Remove all special characters (keep only letters, numbers, and spaces)
# data_table['cleaned_review'] = data_table['review_content'].astype(str).apply(
#     lambda x: re.sub(r'[^A-Za-z0-9\s]', '', x)
# )

# print(data_table[['review_content', 'cleaned_review']].head(10))



# Export cleaned dataset to CSV
data_table.to_csv("datas/cleaned_reviews2.csv", index=False, encoding='utf-8')
