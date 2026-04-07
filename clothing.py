from unittest import result

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

# Load dataset
df = pd.read_csv("myntra.csv")

# Show first 5 rows
print(df.head())

# Show columns
print(df.columns)
# assuming your dataframe name is df
df = df[['name', 'price', 'rating', 'seller', 'discount']]

df.head()
# Check for missing values
print(df.isnull().sum())

df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df['discount'] = pd.to_numeric(df['discount'], errors='coerce')

df = df.dropna()
df = df.reset_index(drop=True)

# 🔥 ADD THIS
df = df.sample(10000, random_state=42)
df = df.reset_index(drop=True)

print(df.shape)


# Create features column
df['features'] = df['name'] + " " + df['seller']

# Show only important columns
print(df[['name', 'seller', 'features']].head())
df = df.sample(10000, random_state=42)
df = df.reset_index(drop=True)


# Create TF-IDF object
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['features'])

print(tfidf_matrix.shape)


def recommend(product_name):
    # find matching product (partial match)
    matches = df[df['name'].str.contains(product_name, case=False, na=False)]

    if matches.empty:
        return "Product not found"

    idx = matches.index[0]

    sim_scores = cosine_similarity(tfidf_matrix[idx], tfidf_matrix)

    scores = list(enumerate(sim_scores[0]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    scores = scores[1:11]

    product_indices = [i[0] for i in scores]

    result = df[['name', 'seller', 'price', 'rating']].iloc[product_indices]
    return result.sort_values(by='rating', ascending=False)


results = recommend("t-shirt")

for i, row in results.iterrows():
    print(
        f" {row['name']} | {row['seller']} | ₹{row['price']} | Rating: {row['rating']}")
