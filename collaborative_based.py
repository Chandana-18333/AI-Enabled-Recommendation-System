import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

data = pd.read_csv('cleaned_data.csv')

data['rating'] = data['rating'].fillna(0)

def collaborative_filtering_recommendations(data, target_user_id, top_n=5):

    user_item_matrix = data.pivot_table(
        index='user_id',
        columns='product_name',
        values='rating',
        aggfunc='mean'
    ).fillna(0)

    user_similarity = cosine_similarity(user_item_matrix)

    user_similarity_df = pd.DataFrame(
        user_similarity,
        index=user_item_matrix.index,
        columns=user_item_matrix.index
    )

    if target_user_id not in user_item_matrix.index:
        return pd.DataFrame()

    similar_users = user_similarity_df[target_user_id].sort_values(ascending=False)[1:]

    recommended_products = []

    for similar_user in similar_users.index:
        similar_user_ratings = user_item_matrix.loc[similar_user]
        target_user_ratings = user_item_matrix.loc[target_user_id]

        products_to_recommend = similar_user_ratings[
            (similar_user_ratings > 0) & (target_user_ratings == 0)
        ]

        recommended_products.extend(products_to_recommend.index.tolist())

        if len(recommended_products) >= top_n:
            break

    recommended_products = list(dict.fromkeys(recommended_products))[:top_n]

    recommended_details = data[data['product_name'].isin(recommended_products)][
        ['product_name', 'brand', 'category', 'price', 'rating']
    ].drop_duplicates().head(top_n)

    return recommended_details


target_user_id = data['user_id'].iloc[0]
top_n = 5

print(f"\nTop {top_n} recommendations for user {target_user_id}:")
print(collaborative_filtering_recommendations(data, target_user_id, top_n))