import pandas as pd
from config import DATA_PATH

def get_rating_based_recommendations(top_n=10, min_reviews=0, data_path=None):
    if data_path is None:
        data_path = DATA_PATH
    """
    Recommend top-rated products for new users based on global average ratings.
    Logic: Group by product -> Take average rating -> Sort descending.
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
    
    # Check if necessary columns exist
    required_cols = ['ProdID', 'Rating']
    for col in required_cols:
        if col not in data.columns:
            return f"Required column '{col}' missing from the dataset."
            
    # Group by product
    # Calculate the average rating, and count the number of ratings
    # Also fetch first instance of category and brand for display
    agg_funcs = {
        'Rating': 'mean',
        "User's ID": 'count', # Use this as rating count
        'Category': 'first',
        'Brand': 'first',
    }
    
    # Add new columns if they exist in the dataset
    if 'Product_Display_Name' in data.columns:
        agg_funcs['Product_Display_Name'] = 'first'
    if 'Description' in data.columns:
        agg_funcs['Description'] = 'first'
    if 'ImageURL' in data.columns:
        agg_funcs['ImageURL'] = 'first'
    if 'Category' not in data.columns:
        agg_funcs.pop('Category', None)
    if 'Brand' not in data.columns:
        agg_funcs.pop('Brand', None)

    product_stats = data.groupby('ProdID').agg(agg_funcs).rename(columns={"User's ID": 'Rating Count'})

    # Optional filtering to ignore products with very few reviews (less reliable ratings)
    if min_reviews > 0:
        product_stats = product_stats[product_stats['Rating Count'] >= min_reviews]
    
    # Sort descending by average rating
    # Secondary sort by 'Rating Count' to break ties
    sorted_products = product_stats.sort_values(by=['Rating', 'Rating Count'], ascending=[False, False])
    
    # Get top_n products
    top_products = sorted_products.head(top_n).reset_index()
    
    # Return all necessary display columns
    cols_to_return = ['ProdID', 'Rating', 'Rating Count']
    if 'Category' in top_products.columns:
        cols_to_return.append('Category')
    if 'Brand' in top_products.columns:
        cols_to_return.append('Brand')
    if 'ImageURL' in top_products.columns:
        cols_to_return.append('ImageURL')
    if 'Product_Display_Name' in top_products.columns:
        cols_to_return.append('Product_Display_Name')
    if 'Description' in top_products.columns:
        cols_to_return.append('Description')

    return top_products[cols_to_return]

if __name__ == "__main__":
    print("Finding generic top-rated recommendations for a new user...")
    # Using min_reviews=2 as a generic threshold so we don't just get obscure 1-rating 5-star items
    recommendations = get_rating_based_recommendations(top_n=5, min_reviews=2)
    print(recommendations)
