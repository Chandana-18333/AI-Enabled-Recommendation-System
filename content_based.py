# content_based.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Load dataset
file_path = 'cleaned_data.csv'
df = pd.read_csv(file_path)

# Fill missing values
df['price'] = df['price'].fillna(df['price'].mean())
df['category'] = df['category'].fillna('')
df['brand'] = df['brand'].fillna('')
df['product_name'] = df['product_name'].fillna('')

# Remove exact duplicate rows to avoid indexing issues
df = df.drop_duplicates(subset=['product_name', 'brand', 'category'])

# Combine text features for content-based filtering
df['features'] = df['brand'] + ' ' + df['category'] + ' ' + df['product_name']

# Vectorize text using TF-IDF
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['features'])

# Compute cosine similarity
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Map product name to list of indices (handle duplicates)
from collections import defaultdict
product_indices = defaultdict(list)
for idx, name in enumerate(df['product_name']):
    product_indices[name].append(idx)

# Recommendation function
def recommend(product_name, num_recommendations=5):
    if product_name not in product_indices:
        print(f"Product '{product_name}' not found in dataset.")
        return pd.DataFrame()
    
    # Use the first index of the product
    idx = product_indices[product_name][0]
    sim_scores = list(enumerate(cosine_sim[idx].flatten()))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Exclude the product itself and limit to available recommendations
    sim_scores = [s for s in sim_scores if s[0] != idx][:num_recommendations]

    recommended_indices = [s[0] for s in sim_scores]
    recommended_products = df.iloc[recommended_indices][['product_name', 'brand', 'category', 'price']]
    return recommended_products

# Test recommendation
test_product = 'Kindle Paperwhite'
print(f"\nRecommendations for '{test_product}':")
print(recommend(test_product, 5))