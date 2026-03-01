import pandas as pd

def preprocess_data(file_path):

    data = pd.read_csv(file_path)
    print("Original Shape:", data.shape)

    data = data.rename(columns={
        "ProductID": "product_id",
        "UserID": "user_id",
        "Rating": "rating",
        "ProductName": "product_name",
        "Brand": "brand",
        "Category": "category",
        "Price": "price"
    })

    data["rating"] = pd.to_numeric(data["rating"], errors="coerce")
    data["price"] = pd.to_numeric(data["price"], errors="coerce")

    data["rating"] = data["rating"].fillna(0)
    data["price"] = data["price"].fillna(data["price"].median())

    for col in ["product_name", "brand", "category"]:
        data[col] = data[col].fillna("Unknown")

    data = data.dropna(subset=["user_id", "product_id"])
    data = data.drop_duplicates()

    print("Cleaned Shape:", data.shape)

    user_item_matrix = data.pivot_table(
        index="user_id",
        columns="product_id",
        values="rating"
    ).fillna(0)

    data.to_csv("cleaned_data.csv", index=False)
    user_item_matrix.to_csv("user_item_matrix.csv")

    print("Preprocessing Completed Successfully")

    return data, user_item_matrix


if __name__ == "__main__":
    preprocess_data("clean_data.csv")