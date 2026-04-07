import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config import DATA_PATH


def get_collaborative_recommendations(user_id, top_n=5, data_path=None):
    """
    Recommend products based on similar users' preferences (collaborative filtering).
    Includes fallback for cold-start and empty results.
    """

    if data_path is None:
        data_path = DATA_PATH

    # =========================
    # 1. Load Data
    # =========================
    try:
        data = pd.read_csv(data_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

    print("Data Loaded:", data.shape)
    print("Columns:", data.columns)
    print("Incoming user_id:", user_id)

    # =========================
    # 2. Standardize Column Names
    # =========================
    column_mapping = {
        "user_id": "User's ID",
        "UserID": "User's ID",
        "product_id": "ProdID",
        "ProductID": "ProdID",
        "rating": "Rating",
    }

    data.rename(columns=column_mapping, inplace=True)

    required_cols = ["User's ID", "ProdID", "Rating"]
    for col in required_cols:
        if col not in data.columns:
            print(f"Missing column: {col}")
            return []

    # =========================
    # 3. Merge Firebase History (Optional)
    # =========================
    try:
        from backend.firebase_db import get_user_history_df

        history_df = get_user_history_df()

        if not history_df.empty:
            history_df.rename(columns=column_mapping, inplace=True)

            history_df["User's ID"] = history_df["User's ID"].astype(data["User's ID"].dtype)
            history_df["ProdID"] = history_df["ProdID"].astype(data["ProdID"].dtype)

            history_df = history_df[["User's ID", "ProdID", "Rating"]]

            data = pd.concat([data, history_df], ignore_index=True)

    except Exception as e:
        print(f"Firebase merge failed: {e}")

    # =========================
    # 4. Handle Cold Start (User Not Found)
    # =========================
    if user_id not in data["User's ID"].values:
        print(f"User {user_id} not found. Showing popular items.")

        fallback = (
            data.sort_values(by="Rating", ascending=False)
            .drop_duplicates(subset=["ProdID"])
            .head(top_n)
        )

        return fallback.to_dict(orient="records")

    # =========================
    # 5. Create User-Item Matrix
    # =========================
    user_item_matrix = data.pivot_table(
        index="User's ID",
        columns="ProdID",
        values="Rating",
        fill_value=0,
    )

    print("Matrix shape:", user_item_matrix.shape)

    # =========================
    # 6. Cosine Similarity
    # =========================
    user_similarity = cosine_similarity(user_item_matrix)

    user_similarity_df = pd.DataFrame(
        user_similarity,
        index=user_item_matrix.index,
        columns=user_item_matrix.index,
    )

    # =========================
    # 7. Find Similar Users
    # =========================
    sim_scores = user_similarity_df[user_id].drop(user_id)

    similar_users = sim_scores.sort_values(ascending=False).head(top_n).index

    print("Similar users:", list(similar_users))

    # =========================
    # 8. Recommend Products
    # =========================
    user_rated_products = user_item_matrix.loc[user_id]

    unrated_products = user_rated_products[user_rated_products == 0].index

    similar_users_ratings = user_item_matrix.loc[similar_users, unrated_products]

    similar_users_ratings = similar_users_ratings.replace(0, np.nan)

    avg_ratings = similar_users_ratings.mean().fillna(0)

    recommended_product_ids = (
        avg_ratings.sort_values(ascending=False)
        .head(top_n)
        .index.tolist()
    )

    print("Recommended IDs:", recommended_product_ids)

    # =========================
    # 9. Fallback if Empty
    # =========================
    if len(recommended_product_ids) == 0:
        print("No recommendations found. Showing popular items.")

        fallback = (
            data.sort_values(by="Rating", ascending=False)
            .drop_duplicates(subset=["ProdID"])
            .head(top_n)
        )

        return fallback.to_dict(orient="records")

    # =========================
    # 10. Get Product Details
    # =========================
    products = data.drop_duplicates(subset=["ProdID"]).set_index("ProdID")

    display_cols = ["Rating"]

    optional_cols = [
        "Tags",
        "Category",
        "Brand",
        "ImageURL",
        "Product_Display_Name",
        "Description",
    ]

    for col in optional_cols:
        if col in products.columns:
            display_cols.append(col)

    try:
        recommended_products = (
            products.loc[recommended_product_ids][display_cols]
            .reset_index()
            .to_dict(orient="records")
        )
    except Exception as e:
        print(f"Error fetching product details: {e}")
        return []

    return recommended_products


# =========================
# TEST RUN
# =========================
if __name__ == "__main__":
    user_to_test = 1705

    result = get_collaborative_recommendations(user_to_test, top_n=5)

    print("\nFinal Output:")
    print(result)