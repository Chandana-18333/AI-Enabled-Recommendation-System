import pandas as pd

data = pd.read_csv('cleaned_data.csv')

data['rating'] = data['rating'].fillna(0)

def rating_based_recommendations(data, top_n=5):

    product_stats = data.groupby('product_name').agg({
        'rating': 'mean',
        'user_id': 'count'
    }).reset_index()

    product_stats.rename(columns={
        'rating': 'average_rating',
        'user_id': 'rating_count'
    }, inplace=True)

    popular_products = product_stats[
        product_stats['rating_count'] > 5
    ].sort_values(
        by=['average_rating', 'rating_count'],
        ascending=False
    )

    top_products = popular_products.head(top_n)

    recommended_details = data[data['product_name'].isin(top_products['product_name'])][
        ['product_name', 'brand', 'category', 'price', 'rating']
    ].drop_duplicates().head(top_n)

    return recommended_details


top_n = 5

print(f"\nTop {top_n} Popular Products:")
print(rating_based_recommendations(data, top_n))