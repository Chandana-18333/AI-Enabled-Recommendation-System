import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import DATA_PATH

def get_content_based_recommendations(product_id, top_n=10, data_path=None):
    if data_path is None:
        data_path = DATA_PATH
    """
    Recommend products similar to a given product using content-based filtering.
    """
    # Load data
    data = pd.read_csv(data_path)
    data.rename(
        columns={
            'ProductID': 'ProdID',
            'product_id': 'ProdID',
            'ProductName': 'Product_Display_Name',
            'UserID': "User's ID",
            'user_id': "User's ID",
        },
        inplace=True,
    )
    
    # For content filtering, we just need unique products and their features
    products = data.drop_duplicates(subset=['ProdID']).copy()
    products.reset_index(drop=True, inplace=True)
    
    if product_id not in products['ProdID'].values:
        return f"Product ID {product_id} not found in the dataset."
        
    # Ensure Tags column has no NaN values
    products['Tags'] = products['Tags'].fillna('')
    
    # 1. Convert "Tags" column -> TF-IDF
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(products['Tags'])
    
    # 2. Apply cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # 3. Find similar products
    # Map product ID to index
    idx = products.index[products['ProdID'] == product_id].tolist()[0]
    
    # Get similarity scores for all products with the target product
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort products based on similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get top_n similar products (excluding the product itself)
    sim_scores = sim_scores[1:top_n+1]
    
    # Get product indices
    product_indices = [i[0] for i in sim_scores]
    
    # Return similar products
    display_cols = ['ProdID', 'Tags', 'Category', 'Brand', 'ImageURL', 'Rating']
    if 'Product_Display_Name' in products.columns:
        display_cols.append('Product_Display_Name')
    if 'Description' in products.columns:
        display_cols.append('Description')
        
    return products.iloc[product_indices][display_cols]

if __name__ == "__main__":
    # Example usage (assuming Product 2 exists in cleaned_data.csv)
    print("Finding products similar to ProdID 2...")
    recommendations = get_content_based_recommendations(product_id=2, top_n=5)
    print(recommendations)
