import reflex as rx
import pandas as pd
import os
from typing import List, Dict, Any
from config import DATA_PATH


class ProductsState(rx.State):
    """State for fetching and displaying products."""

    all_products: List[Dict[str, Any]] = []
    search_query: str = ""
    sort_order: str = "default"

    def fetch_products(self):
        print("📂 DATA PATH:", DATA_PATH)

        # =========================
        # 1. Check File Exists
        # =========================
        if not os.path.exists(DATA_PATH):
            print("❌ DATA FILE NOT FOUND")

            self.all_products = [
                {
                    "ProdID": 1,
                    "Product_Display_Name": "Sample Product",
                    "Brand": "Demo",
                    "Category": "Test",
                    "Price": "999.00",
                    "Rating": "4.5",
                    "ImageURL": "/placeholder.jpg",
                }
            ]
            return

        try:
            # =========================
            # 2. Load Data
            # =========================
            data = pd.read_csv(DATA_PATH)
            print("✅ Data Loaded:", data.shape)
            print("🧾 Columns:", list(data.columns))

            # =========================
            # 3. Standardize Columns
            # =========================
            data.rename(
                columns={
                    "ProductID": "ProdID",
                    "product_id": "ProdID",
                    "UserID": "User's ID",
                    "user_id": "User's ID",
                    "ProductName": "Product_Display_Name",
                },
                inplace=True,
            )

            if "ProdID" not in data.columns:
                print("❌ ProdID column missing")
                self.all_products = []
                return

            # =========================
            # 4. Remove Duplicates
            # =========================
            unique_products = data.drop_duplicates(subset=["ProdID"]).copy()

            print("🛍️ Unique products:", len(unique_products))

            if unique_products.empty:
                print("⚠️ No products found after cleaning")

                self.all_products = [
                    {
                        "ProdID": 0,
                        "Product_Display_Name": "No Products Found",
                        "Brand": "",
                        "Category": "",
                        "Price": "0.00",
                        "Rating": "N/A",
                        "ImageURL": "/placeholder.jpg",
                    }
                ]
                return

            # =========================
            # 5. Generate Price
            # =========================
            import binascii

            unique_products["Price_Num"] = unique_products["ProdID"].astype(str).apply(
                lambda x: (binascii.crc32(x.encode("utf-8")) % 2500) + 499
            )

            # =========================
            # 6. Apply Search Filter
            # =========================
            if self.search_query:
                mask = False

                if "Brand" in unique_products.columns:
                    mask = mask | unique_products["Brand"].astype(str).str.contains(
                        self.search_query, case=False, na=False
                    )

                if "Category" in unique_products.columns:
                    mask = mask | unique_products["Category"].astype(str).str.contains(
                        self.search_query, case=False, na=False
                    )

                if "Product_Display_Name" in unique_products.columns:
                    mask = mask | unique_products[
                        "Product_Display_Name"
                    ].astype(str).str.contains(self.search_query, case=False, na=False)

                unique_products = unique_products[mask]

            # =========================
            # 7. Apply Sorting
            # =========================
            if self.sort_order == "low_to_high":
                unique_products = unique_products.sort_values("Price_Num", ascending=True)
            elif self.sort_order == "high_to_low":
                unique_products = unique_products.sort_values("Price_Num", ascending=False)

            # =========================
            # 8. Format Data
            # =========================
            unique_products = unique_products.head(48).fillna("")

            unique_products["Price"] = unique_products["Price_Num"].apply(
                lambda x: f"{x}.00"
            )

            if "ImageURL" in unique_products.columns:
                unique_products["ImageURL"] = unique_products["ImageURL"].apply(
                    lambda x: str(x).split(" | ")[0]
                    if pd.notnull(x) and str(x) != ""
                    else "/placeholder.jpg"
                )
            else:
                unique_products["ImageURL"] = "/placeholder.jpg"

            if "Rating" in unique_products.columns:
                unique_products["Rating"] = unique_products["Rating"].apply(
                    lambda x: f"{float(x):.1f}"
                    if pd.notnull(x) and str(x) != ""
                    else "N/A"
                )
            else:
                unique_products["Rating"] = "N/A"

            # =========================
            # 9. Final Assignment
            # =========================
            self.all_products = unique_products.to_dict("records")

            print("✅ Products ready:", len(self.all_products))

        except Exception as e:
            print(f"❌ Error fetching products: {e}")

            self.all_products = [
                {
                    "ProdID": 999,
                    "Product_Display_Name": "Error Loading Products",
                    "Brand": "",
                    "Category": "",
                    "Price": "0.00",
                    "Rating": "N/A",
                    "ImageURL": "/placeholder.jpg",
                }
            ]

    # =========================
    # UI Actions
    # =========================
    def update_sort(self, val: str):
        self.sort_order = val
        return self.fetch_products()

    def update_search(self, q: str):
        self.search_query = q
        return self.fetch_products()

    def handle_search_submit(self, form_data: Dict[str, Any]):
        query = form_data.get("q", "")
        return rx.redirect(f"/?q={query}")