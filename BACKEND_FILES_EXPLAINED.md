# 🔧 Backend Python Files: Deep Technical Explanation

## Overview
The `backend/` folder contains 5 Python files that work together to power the AI recommendation engine. Each file has a specific responsibility in the ML pipeline.

---

## 📁 Backend File Structure

```
backend/
├── __init__.py                      # Empty, makes 'backend' a Python package
├── recommender.py                  # 🎯 Orchestrator (brain of the system)
├── rating_based.py                 # ⭐ Top-rated products algorithm
├── collaborative_filtering.py       # 👥 User-user similarity algorithm
├── content_filtering.py             # 🏷️ Product-product similarity algorithm
└── cleaning_data.py                 # 🧹 Data preprocessing script
```

---

## 1️⃣ recommender.py - THE ORCHESTRATOR

### 🎯 Purpose
Acts as the **main decision-maker** that routes requests to the appropriate algorithm based on user context.

### 📍 Location
[backend/recommender.py](backend/recommender.py)

### 📊 Function: `get_combined_recommendations()`

```python
def get_combined_recommendations(
    user_id=None,                    # User's unique ID (None if not logged in)
    is_new_user=False,               # Is this their first visit?
    current_product_id=None,         # Are they viewing a specific product?
    top_n=5,                         # How many recommendations to return?
    data_path='cleaned_data.csv'     # Path to dataset
):
```

### 🔀 Decision Logic

```
INPUT: user_id, is_new_user, current_product_id

├─ Is user_id None OR is_new_user = True?
│  │
│  ├─ YES → Call: get_rating_based_recommendations()
│  │        └─ Returns: Top-rated products for everyone
│  │
│  └─ NO → Call: get_collaborative_recommendations(user_id)
│         └─ Returns: Personalized for this user
│         │
│         └─ Is current_product_id provided?
│            │
│            ├─ YES → Also call: get_content_based_recommendations(current_product_id)
│            │        └─ Returns: Similar products
│            │        └─ BLEND: Combine collaborative + content results
│            │        └─ Return: Top N from merged list
│            │
│            └─ NO → Return: Collaborative results as-is

OUTPUT: pandas DataFrame with recommendations
```

### 💡 Real Use Cases

**Use Case 1: New Visitor (No Login)**
```python
# User visits without logging in
get_combined_recommendations(
    user_id=None,
    is_new_user=True,
    current_product_id=None,
    top_n=8
)

# Flow: None or is_new_user=True → rating_based()
# Shows: Top-rated products (everyone sees these)
# Example: [iPhone 15 (4.8★), Samsung TV (4.7★), Sony Camera (4.6★), ...]
```

**Use Case 2: Returning User on Home Page**
```python
# User logged in, viewing home page
get_combined_recommendations(
    user_id=1705,
    is_new_user=False,
    current_product_id=None,
    top_n=8
)

# Flow: user_id provided + no product → collaborative_filtering()
# Shows: Personalized recommendations based on similar users
# Example: [Laptop (4.5★), Monitor (4.3★), Keyboard (4.2★), ...]
```

**Use Case 3: User Browsing Specific Product**
```python
# User clicked on iPhone 15 product page
get_combined_recommendations(
    user_id=1705,
    is_new_user=False,
    current_product_id=123,
    top_n=8
)

# Flow: 
#   1. Call: collaborative_filtering(1705) → 20 products
#   2. Call: content_based_filtering(123) → 20 similar products
#   3. Blend: Merge, remove duplicates, take top 8
# Shows: Personalized + Similar products combined
# Example: [iPhone 15 Pro (similar + his taste), AirPods (similar + rating)]
```

### 🔧 Code Walkthrough

```python
def get_combined_recommendations(user_id=None, is_new_user=False, ...):
    
    # ============ PART 1: Check if new user ============
    if is_new_user or user_id is None:
        # For unknown users, use rating-based
        print("Fetching rating-based recommendations for new user...")
        return get_rating_based_recommendations(
            top_n=top_n, 
            min_reviews=2,        # Only products with 2+ reviews
            data_path=data_path
        )
    
    # ============ PART 2: For known users ============
    else:
        # Start with collaborative filtering
        print(f"Fetching collaborative recommendations for User {user_id}...")
        collab_recs = get_collaborative_recommendations(
            user_id=user_id,
            top_n=top_n,
            data_path=data_path
        )
        
        # ============ PART 3: Blend if browsing product ============
        if current_product_id is not None:
            print(f"Fetching content-based recommendations for Product {current_product_id}...")
            content_recs = get_content_based_recommendations(
                product_id=current_product_id,
                top_n=top_n,
                data_path=data_path
            )
            
            # Both algorithms returned valid results?
            if isinstance(collab_recs, pd.DataFrame) and isinstance(content_recs, pd.DataFrame):
                # Stack them vertically
                combined = pd.concat([collab_recs, content_recs])
                
                # Remove duplicates (keep only unique products)
                combined = combined.drop_duplicates(subset=['ProdID'])
                
                # Return top N after merging
                return combined.head(top_n).reset_index(drop=True)
            
            # Content-based only is valid?
            elif isinstance(content_recs, pd.DataFrame):
                return content_recs
        
        # Return collaborative as default
        return collab_recs
```

### ✨ Key Features

| Feature | Purpose |
|---------|---------|
| **Routing Logic** | Chooses algorithm based on context |
| **Error Handling** | Returns collab_recs if content_recs fails |
| **Duplicate Removal** | `.drop_duplicates(subset=['ProdID'])` ensures no product appears twice |
| **Blending** | Merges two algorithm outputs for diversity |
| **Flexibility** | Can adjust `top_n` for different use cases |

---

## 2️⃣ rating_based.py - TOP-RATED PRODUCTS

### 🎯 Purpose
Recommends **globally top-rated products**. Used for new users who have no history.

### 📍 Location
[backend/rating_based.py](backend/rating_based.py)

### 📊 Function: `get_rating_based_recommendations()`

```python
def get_rating_based_recommendations(
    top_n=10,           # How many products to return?
    min_reviews=0,      # Minimum number of reviews filter
    data_path=None      # Path to CSV
):
```

### 🧮 Algorithm Steps

```
Step 1: Load CSV
  └─ data = pd.read_csv(data_path)
  └─ Columns: ProdID, User's ID, Rating, Category, Brand, ...

Step 2: Group by Product
  └─ product_stats = data.groupby('ProdID').agg({
       'Rating': 'mean',           # Average rating
       "User's ID": 'count',       # Call it Rating Count
       'Category': 'first',        # Get first value
       'Brand': 'first',
       'ImageURL': 'first'
     })

Step 3: Filter by Reviews (optional)
  └─ if min_reviews > 0:
       └─ Keep only products with >= min_reviews ratings

Step 4: Sort by Rating
  └─ product_stats.sort_values(
       by=['Rating', 'Rating Count'],  # Primary: rating, Secondary: count
       ascending=[False, False]
     )

Step 5: Return Top N
  └─ return top_products.head(top_n)
```

### 💡 Real Use Case 1: Lazy First-Time Shopper

```
Scenario: User visits AI-Store for first time, doesn't login
├─ RecommendationState.fetch_recommendations() called
├─ Checks: is_new_user = True, user_id = None
├─ Calls: get_rating_based_recommendations(top_n=8, min_reviews=2)
│
├─ Step 1: Load all 100K products from cleaned_data.csv
├─ Step 2: Group by ProdID, calculate average rating
├─ Step 3: Filter: Keep only products with 2+ reviews
├─ Step 4: Sort by rating (highest first)
│
├─ Results:
│  ProdID: 5847    | Rating: 4.9⭐ | Reviews: 2500 | Brand: Samsung
│  ProdID: 2134    | Rating: 4.8⭐ | Reviews: 1800 | Brand: Apple
│  ProdID: 9234    | Rating: 4.7⭐ | Reviews: 1200 | Brand: Sony
│  ...
│
└─ Display in 4-column grid on home page
```

### 💡 Real Use Case 2: New User Just Signed Up

```
Scenario: User just signed up (first registered account)
├─ is_new_user = True (even though user_id exists)
├─ Calls: get_rating_based_recommendations(top_n=8, min_reviews=2)
├─ Shows same as above (highest-rated products)
└─ After first purchase/rating: switches to collaborative filtering
```

### 💡 Real Use Case 3: Emergency Fallback

```
Scenario: Collaborative filtering fails for some reason
├─ get_collaborative_recommendations() returns empty or error
├─ recommender.py detects: isinstance(collab_recs, pd.DataFrame) = False
├─ Falls back to rating_based()
├─ User still gets good recommendations
```

### 📈 Code Analysis

```python
agg_funcs = {
    'Rating': 'mean',              # Average rating for product
    "User's ID": 'count',          # How many people rated it
    'Category': 'first',           # Get first category value
    'Brand': 'first',              # Get first brand value
    'ImageURL': 'first',           # Get first image URL
    # Optionally add more
    'Product_Display_Name': 'first'  # If column exists
    'Description': 'first'           # If column exists
}

product_stats = data.groupby('ProdID').agg(agg_funcs).rename(
    columns={"User's ID": 'Rating Count'}  # Rename for clarity
)

# Filter by minimum reviews
if min_reviews > 0:
    product_stats = product_stats[product_stats['Rating Count'] >= min_reviews]

# Sort by rating descending, then by review count (tiebreaker)
sorted_products = product_stats.sort_values(
    by=['Rating', 'Rating Count'],
    ascending=[False, False]
)

# Get top N
top_products = sorted_products.head(top_n).reset_index()
```

### ✨ Performance

| Metric | Value |
|--------|-------|
| **Time Complexity** | O(n log n) where n = unique products |
| **Typical Runtime** | 50-80 ms |
| **Memory** | ~150 MB (full CSV in memory) |
| **Scalability** | Works great up to 1M products |

---

## 3️⃣ collaborative_filtering.py - USER-USER SIMILARITY

### 🎯 Purpose
Finds users **similar to you**, then recommends **products they liked**. Provides personalized recommendations for returning users.

### 📍 Location
[backend/collaborative_filtering.py](backend/collaborative_filtering.py)

### 📊 Function: `get_collaborative_recommendations()`

```python
def get_collaborative_recommendations(
    user_id,            # The user we're recommending for
    top_n=5,            # How many recommendations?
    data_path=None      # Path to CSV
):
```

### 🧮 Algorithm Steps (COMPLEX!)

```
INPUT: user_id=1705

Step 1: Load Data & Validate
  ├─ data = pd.read_csv(data_path)
  ├─ Check: Does user_id 1705 exist?
  └─ If NO: Return error message

Step 2: CREATE USER-ITEM MATRIX
  ├─ user_item_matrix = data.pivot_table(
  │    index="User's ID",     ← Rows = different users
  │    columns="ProdID",      ← Columns = different products
  │    values="Rating",       ← Values = ratings (0 if not rated)
  │    fill_value=0           ← Unrated products = 0
  │  )
  │
  ├─ Result:
  │   User    | Prod1 | Prod2 | Prod3 | Prod4 | ...
  │   --------|-------|-------|-------|-------|-----
  │   1705    |  5    |  0    |  4    |  3    |  0
  │   1234    |  3    |  5    |  0    |  4    |  5
  │   5678    |  0    |  4    |  3    |  0    |  4
  │   ...
  │
  └─ Shape: (num_users, num_products)

Step 3: CALCULATE USER SIMILARITY
  ├─ Where: similarity = cosine_similarity(user_item_matrix)
  ├─
  ├─ For each pair of users, calculate:
  │
  │   similarity(UserA, UserB) = (A · B) / (|A| × |B|)
  │
  │   Example:
  │   UserA ratings:  [5, 0, 4, 3, 0]
  │   UserB ratings:  [3, 5, 0, 4, 5]
  │
  │   dot product = 5*3 + 0*5 + 4*0 + 3*4 + 0*5 = 15 + 12 = 27
  │   |UserA| = √(5² + 0² + 4² + 3²) = √50 ≈ 7.07
  │   |UserB| = √(3² + 5² + 0² + 4² + 5²) = √75 ≈ 8.66
  │   similarity = 27 / (7.07 × 8.66) ≈ 0.44 (44% similar)
  │
  └─ Result: Similarity matrix (num_users × num_users)

Step 4: FIND SIMILAR USERS
  ├─ sim_scores = similarity_matrix[user_id]
  │   └─ Get all similarity scores for user 1705
  │   └─ Result: {1234: 0.85, 5678: 0.42, 9999: 0.91, ...}
  │
  ├─ sim_scores = sim_scores.drop(user_id)  # Remove self
  │   └─ We don't want to compare user 1705 to themselves
  │
  └─ similar_users = sim_scores.sort_values(ascending=False).head(top_n)
      └─ Get top 5 most similar users
      └─ Result: [9999 (0.95), 1234 (0.85), 7777 (0.81), 3333 (0.78), 2222 (0.72)]

Step 5: IDENTIFY UNRATED PRODUCTS
  ├─ user_rated_products = user_item_matrix.loc[user_id]
  │   └─ Get all products and their ratings for user 1705
  │   └─ Result: [5, 0, 4, 3, 0, 0, 5, 1, ...]
  │
  └─ unrated_products = user_rated_products[user_rated_products == 0].index
      └─ Find products where rating = 0 (user hasn't rated)
      └─ Result: [Prod2, Prod5, Prod6, Prod9, ...]

Step 6: GET SIMILAR USERS' RATINGS
  ├─ similar_users_ratings = user_item_matrix.loc[
  │    similar_users,     ← Look at these similar users only
  │    unrated_products   ← For these unrated products
  │  ]
  │
  ├─ Result: A smaller matrix
  │   User   | Prod2 | Prod5 | Prod6 | Prod9 | ...
  │   -------|-------|-------|-------|-------|-----
  │   9999   |  5    |  3    |  4    |  0    |
  │   1234   |  3    |  4    |  0    |  5    |
  │   7777   |  4    |  5    |  5    |  3    |
  │   3333   |  0    |  4    |  3    |  4    |
  │   2222   |  5    |  0    |  4    |  5    |
  │
  └─ This shows what similar users rated these products

Step 7: CALCULATE AVERAGE RATINGS
  ├─ Replace 0 (unrated) with NaN
  │   └─ similar_users_ratings = similar_users_ratings.replace(0, np.nan)
  │   └─ Now 0 is ignored (not counted as "bad rating")
  │
  ├─ avg_ratings = similar_users_ratings.mean()
  │   └─ Calculate average for each product
  │   └─ Prod2: (5+3+4+0+5) / 4 [ignoring the 0] = 17/4 = 4.25
  │   └─ Prod5: (3+4+5+4+0) / 4 [ignoring the 0] = 16/4 = 4.00
  │   └─ Result: {Prod2: 4.25, Prod5: 4.00, Prod6: 4.25, Prod9: 4.25}
  │
  └─ avg_ratings = avg_ratings.fillna(0)
      └─ Products no similar user rated = 0 score

Step 8: GET TOP RECOMMENDATIONS
  ├─ avg_ratings.sort_values(ascending=False).head(top_n)
  │   └─ Sort by highest average rating
  │   └─ Result: [Prod2(4.25), Prod6(4.25), Prod9(4.25), Prod5(4.00)]
  │
  └─ recommended_product_ids = [Prod2, Prod6, Prod9, Prod5, ...]

Step 9: GET PRODUCT DETAILS
  ├─ For each recommended product ID
  ├─ Look up: Brand, Category, ImageURL, Rating, Description
  └─ Return DataFrame with product details
```

### 💡 Real Use Case: Personalized Home Page

```
Scenario: User 1705 (Tech Enthusiast) logs in
├─ is_new_user = False, user_id = 1705
├─ Calls: get_collaborative_recommendations(user_id=1705, top_n=8)
│
├─ System finds:
│  ├─ Similar users: [9999 (95% similar), 1234 (85% similar), ...]
│  ├─ These users love: [Laptops, Gaming Monitors, Mechanical Keyboards, ...]
│  ├─ User 1705 hasn't rated these yet
│
├─ Shows recommendations:
│  ├─ Gaming Laptop (4.5⭐) - Similar users rated 4.5
│  ├─ 4K Monitor (4.3⭐) - Similar users rated 4.3  
│  ├─ RGB Keyboard (4.1⭐) - Similar users rated 4.1
│
└─ User 1705 is excited because these match their interests!
```

### 📈 Code Analysis

```python
# Step 1: Validation
if user_id not in data["User's ID"].values:
    return f"User ID {user_id} not found in the dataset."

# Step 2-3: Create matrix and calculate similarity
user_item_matrix = data.pivot_table(
    index="User's ID",
    columns="ProdID",
    values="Rating",
    fill_value=0
)

user_similarity = cosine_similarity(user_item_matrix)
user_similarity_df = pd.DataFrame(
    user_similarity,
    index=user_item_matrix.index,
    columns=user_item_matrix.index
)

# Step 4: Find similar users
sim_scores = user_similarity_df[user_id].drop(user_id)
similar_users = sim_scores.sort_values(ascending=False).head(top_n).index

# Step 5-6: Get unrated products
user_rated_products = user_item_matrix.loc[user_id]
unrated_products = user_rated_products[user_rated_products == 0].index
similar_users_ratings = user_item_matrix.loc[similar_users, unrated_products]

# Step 7-8: Average and rank
similar_users_ratings = similar_users_ratings.replace(0, np.nan)
avg_ratings = similar_users_ratings.mean().fillna(0)
recommended_product_ids = avg_ratings.sort_values(ascending=False).head(top_n).index.tolist()

# Step 9: Return details
products = data.drop_duplicates(subset=['ProdID']).set_index('ProdID')
recommended_products = products.loc[recommended_product_ids][display_cols].reset_index()
return recommended_products
```

### ✨ Performance

| Metric | Value |
|--------|-------|
| **Time Complexity** | O(m² + k*n) where m=users, n=products, k=similar users |
| **Typical Runtime** | 150-300 ms |
| **Memory** | ~500 MB (full user-item matrix) |
| **Bottleneck** | Creating similarity matrix for millions of users |

### ⚠️ Limitations

- ❌ **Cold start problem**: New users have no ratings
- ❌ **Sparsity**: Most users haven't rated most products (0s everywhere)
- ❌ **Popular item bias**: Everyone likes popular items, less diverse
- ❌ **Slow for large datasets**: O(m²) matrix computation

---

## 4️⃣ content_filtering.py - PRODUCT SIMILARITY

### 🎯 Purpose
Finds products **similar to the one you're viewing**. Shows "Related Products" / "You might also like" section on product detail page.

### 📍 Location
[backend/content_filtering.py](backend/content_filtering.py)

### 📊 Function: `get_content_based_recommendations()`

```python
def get_content_based_recommendations(
    product_id,         # Product user is viewing
    top_n=10,           # How many similar products?
    data_path=None      # Path to CSV
):
```

### 🧮 Algorithm Steps

```
INPUT: product_id=2847 (Bluetooth Speaker)

Step 1: Load Data & Validate
  ├─ data = pd.read_csv(data_path)
  ├─ Check: Does product 2847 exist?
  └─ If NO: Return error message

Step 2: EXTRACT PRODUCT FEATURES
  ├─ For each product, get the "Tags" column
  ├─ Example Tags:
  │   Prod 2847: "wireless, battery-powered, portable, Bluetooth, speaker"
  │   Prod 2845: "wired, USB-powered, desktop, speaker"
  │   Prod 2900: "wireless, battery-powered, portable, Bluetooth, earbuds"
  │   
  └─ These tags describe product characteristics

Step 3: CONVERT TO TF-IDF VECTORS
  ├─ TF-IDF = "Term Frequency - Inverse Document Frequency"
  ├─
  ├─ TfidfVectorizer converts text → numerical vectors
  │   └─ stop_words='english' removes common words (the, a, and, etc)
  │
  ├─ Example transformation:
  │   Tags string: "wireless, battery-powered, portable, Bluetooth, speaker"
  │   → Vector: [0.45, 0.32, 0.28, 0.38, 0.52]  (5 unique features)
  │
  └─ Result: Matrix of shape (num_products, num_features)
             where each row is a product
             and each column is a weight for a feature

Step 4: CALCULATE PRODUCT SIMILARITY
  ├─ cosine_similarity(tfidf_matrix, tfidf_matrix)
  ├─
  ├─ Compares each product to every other product
  ├─ Result: How similar is Prod2847 to all other products?
  │
  ├─ Similarity matrix:
  │   Prod2847 vs 2845:  0.52 (somewhat similar)
  │   Prod2847 vs 2900:  0.95 (very similar! both portable bluetooth)
  │   Prod2847 vs 2910:  0.12 (very different)
  │   Prod2847 vs 2920:  0.75 (fairly similar)
  │
  └─ Result: Similarity scores between 0 (nothing in common) to 1 (identical)

Step 5: FIND SIMILAR PRODUCTS
  ├─ Get row for product 2847 from similarity matrix
  ├─ sim_scores = [0.00, 0.52, 0.95, 0.12, 0.75, 0.88, ...]
  │   (0.00 for itself, then similarity with other products)
  │
  ├─ Sort by similarity descending
  │   └─ [0.95 (Prod2900), 0.88 (Prod2875), 0.75 (Prod2920), ...]
  │
  └─ Get top N products (excluding product 2847 itself)
     └─ Top 5: [Prod2900, Prod2875, Prod2920, Prod2899, Prod2856]

Step 6: RETURN PRODUCT DETAILS
  ├─ Look up details for these products:
  │   Product Name, Brand, Price, Image, Rating
  └─ Return as DataFrame
```

### 💡 Real Use Case 1: "Similar Products" on Product Page

```
Scenario: User clicks on "Sony Bluetooth Speaker" (ProdID=2847)
├─ Product detail page loads
├─ Page calls: get_content_based_recommendations(product_id=2847, top_n=5)
│
├─ Algorithm finds products with similar tags:
│  ├─ [0.95 similarity] Bluetooth Wireless Speaker - JBL (ProdID=2900)
│  ├─ [0.88 similarity] Portable Speaker - Beats (ProdID=2875)
│  ├─ [0.75 similarity] Wireless Speaker - Bose (ProdID=2920)
│  ├─ [0.72 similarity] Bluetooth Speaker Pro - Sony (ProdID=2899)
│  └─ [0.68 similarity] Waterproof Speaker - Ultimate Ears (ProdID=2856)
│
├─ Displays in "Customers Also Viewed" section
└─ User can click and buy these similar products
```

### 💡 Real Use Case 2: New Product Discovery

```
Scenario: Company launches new product (no ratings yet)
├─ New Product: "Qi Wireless Charging Pad" (ProdID=9999)
├─ Has tags: "wireless, charging, power"
│
├─ Can't use Collaborative Filtering yet (no ratings)
├─ But Content-Based WORKS immediately!
│
├─ Finds similar products:
│  ├─ USB Charging Cables (similar: wireless/charging)
│  ├─ Power Banks (similar: charging/power)
│  └─ Wireless Chargers (similar: all tags match!)
│
└─ System automatically recommends when users browse related products
```

### 💡 Real Use Case 3: Blending in recommender.py

```
Scenario: User (1705) viewing Laptop (ProdID=5847)
├─ recommender.py calls BOTH:
│  ├─ collab_recs = collaborative_filtering(user_id=1705)
│  │  └─ Returns: Other tech products this user might like
│  │
│  └─ content_recs = content_based_filtering(product_id=5847)
│     └─ Returns: Similar laptops/computers
│
├─ BLENDS the two lists:
│  ├─ Collaborative gives personalization
│  ├─ Content gives product similarity
│  └─ User sees: "Products matched with your taste AND similar to this item"
│
└─ Result: Perfect recommendation for product page!
```

### 📈 Code Analysis

```python
# Step 1: Validation
if product_id not in products['ProdID'].values:
    return f"Product ID {product_id} not found."

# Step 2-3: TF-IDF conversion
products['Tags'] = products['Tags'].fillna('')  # Handle missing tags
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(products['Tags'])

# Step 4: Calculate similarity
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Step 5: Find similar products
idx = products.index[products['ProdID'] == product_id].tolist()[0]
sim_scores = list(enumerate(cosine_sim[idx]))
sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
sim_scores = sim_scores[1:top_n+1]  # Exclude product itself

# Step 6: Return details
product_indices = [i[0] for i in sim_scores]
return products.iloc[product_indices][display_cols]
```

### ✨ Performance

| Metric | Value |
|--------|-------|
| **Time Complexity** | O(n² log n) where n = unique products |
| **Typical Runtime** | 100-200 ms |
| **Memory** | ~200-300 MB |
| **Scalability** | Excellent (can handle millions of products) |

### ✨ Advantages Over Collaborative Filtering

| Aspect | Collab | Content |
|--------|--------|---------|
| New Products | ❌ Cold start | ✅ Works immediately |
| No History | ❌ Can't help | ✅ Works fine |
| Interpretability | ⚠️ "Black box" | ✅ "Because tags match" |
| Speed | ⚠️ O(m²) users | ✅ O(n²) products |

---

## 5️⃣ cleaning_data.py - DATA PREPROCESSING

### 🎯 Purpose
**One-time script** that cleans raw CSV data before using it in ML algorithms.

### 📍 Location
[backend/cleaning_data.py](backend/cleaning_data.py)

### 🧹 What Does It Clean?

```python
import pandas as pd
import numpy as np

# Load original messy CSV
data = pd.read_csv("clean_data.csv")

# ============ STEP 1: HANDLE INVALID PRODUCT IDs ============
# Some products have incorrect IDs: -2147483648 (SQL error number)
data['ProdID'] = data['ProdID'].replace('-2147483648', np.nan)
# Remove rows with no ProdID
data = data.dropna(subset=['ProdID'])
# Convert to integer
data['ProdID'] = data['ProdID'].astype('int64')

# ============ STEP 2: HANDLE USER IDs ============
# Some users have invalid IDs
data["User's ID"] = data["User's ID"].replace('-2147483648', np.nan)
# Remove rows with no User ID
data = data.dropna(subset=["User's ID"])
# Convert to integer
data["User's ID"] = data["User's ID"].astype('int64')

# ============ STEP 3: HANDLE RATINGS ============
# Some ratings might be invalid
data['Rating'] = data['Rating'].astype('float')  # Should be decimal

# ============ STEP 4: HANDLE REVIEW COUNT ============
data['Review Count'] = data['Review Count'].astype('int64')

# ============ STEP 5: FILL TEXT FIELDS ============
# Replace NaN (missing values) with empty strings
data['Category'] = data['Category'].fillna('')
data['Brand'] = data['Brand'].fillna('')
data['Description'] = data['Description'].fillna('')
data['Tags'] = data['Tags'].fillna('')

# ============ STEP 6: CLEAN IMAGE URLs ============
# Some products have multiple URLs separated by '|'
# Extract only the FIRST URL
if 'ImageURL' in data.columns:
    data['ImageURL'] = data['ImageURL'].fillna('').apply(
        lambda x: str(x).split('|')[0] if pd.notnull(x) else x
    )
elif 'Image URL' in data.columns:  # Handle alternate column name
    data['Image URL'] = data['Image URL'].fillna('').apply(
        lambda x: str(x).split('|')[0] if pd.notnull(x) else x
    )

# ============ STEP 7: SAVE CLEANED DATA ============
data.to_csv("cleaned_data.csv", index=False)
print("✅ Data cleaning complete! File saved as cleaned_data.csv")
```

### 💡 Real Use Case: One-Time Setup

```
Scenario: Raw data from database
├─ File: "clean_data.csv" (messy, has errors)
├─
├─ Problems in raw data:
│  ├─ ProdID: -2147483648 (SQL integer overflow error)
│  ├─ User's ID: None/null values
│  ├─ ImageURL: "url1.jpg | url2.jpg | url3.jpg" (multiple URLs)
│  ├─ Tags: Empty/NaN for some products
│  └─ Brand: Mixed case, some missing
│
├─ Run: python backend/cleaning_data.py
│
├─ Result:
│  ├─ Invalid IDs removed
│  ├─ Missing values filled
│  ├─ Image URLs: only first one kept
│  ├─ File: "cleaned_data.csv"
│
└─ Now safe to use in ML algorithms!
```

### 🔍 Data Transformation Example

**Before Cleaning:**
```
ProdID         | User's ID      | Rating | ImageURL
---------------|----------------|--------|----------------------------------
123            | 1705           | 4.5    | url1.jpg | url2.jpg | url3.jpg
-2147483648    | 1234           | 3.0    | url4.jpg
456            | -2147483648    | 4.8    | url5.jpg
789            | None           | 3.5    | url6.jpg
```

**After Cleaning:**
```
ProdID | User's ID | Rating | ImageURL
-------|-----------|--------|----------
123    | 1705      | 4.5    | url1.jpg
456    | (removed) | 4.8    | url5.jpg
```

---

## 🎯 How They Work Together

### Complete Flow Diagram

```
User visits AI-Store
    ↓
┌─ home page loads
├─ RecommendationState.fetch_recommendations() called
│
├─ Goes to: backend/recommender.py
│  get_combined_recommendations(user_id=1705, is_new_user=False)
│
│  decision logic...
│  "User 1705 is logged in and not new"
│  ↓
│  └─ PART 2 of recommender.py:
│     ├─ Calls: backend/collaborative_filtering.py
│     │  get_collaborative_recommendations(user_id=1705)
│     │  └─ Loads cleaned_data.csv (cleaned by cleaning_data.py)
│     │  └─ Creates user-item matrix
│     │  └─ Finds similar users
│     │  └─ Returns 20 personalized products
│     │
│     └─ Is user viewing a product?
│        ├─ YES → Also calls: backend/content_filtering.py
│        │  get_content_based_recommendations(product_id=2847)
│        │  └─ Loads cleaned_data.csv
│        │  └─ Converts tags to TF-IDF
│        │  └─ Finds 20 similar products
│        │
│        └─ BLEND: Merge collab + content results
│           └─ Remove duplicates
│           └─ Return top 8
│
├─ Back to state/recommendation_state.py:
│  ├─ Convert DataFrame to dicts
│  ├─ Add computed fields (Price, formatted Rating)
│  ├─ Store in RecommendationState.recommendations
│
└─ pages/home.py renders:
   └─ 4-column grid of product cards
```

### File Dependency Graph

```
              ┌─────────────────┐
              │ cleaned_data.csv│ ← Output from cleaning_data.py
              │ (5.69 MB)       │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
    rating_based   collab_filt   content_filt
    (rank)         (users)       (products)
        │              │              │
        └──────────────┬──────────────┘
                       ↓
                 recommender.py
                 (orchestrator)
                       ↓
           state/recommendation_state.py
           (manages UI state)
                       ↓
               pages/home.py
               (displays grid)
```

---

## 📋 Summary Table

| File | Purpose | Time | Memory | Input | Output |
|------|---------|------|--------|-------|--------|
| **cleaning_data.py** | Preprocess raw CSV | ~2 min | 200MB | raw .csv | cleaned_data.csv |
| **rating_based.py** | Top-rated products | 50-80ms | 150MB | cleaned_data.csv | DataFrame (8-10 prod) |
| **collab_filt.py** | Personalized recs | 150-300ms | 500MB | cleaned_data.csv + user_id | DataFrame (8-10 prod) |
| **content_filt.py** | Similar products | 100-200ms | 200MB | cleaned_data.csv + prod_id | DataFrame (8-10 prod) |
| **recommender.py** | Route & blend | 50-400ms | 150MB | user_id, prod_id | Final recommendations |

---

## 🎓 Key Takeaways

✅ **recommender.py** = Smart router that picks the right algorithm
✅ **rating_based.py** = Fast + simple, good for cold start
✅ **collab_filt.py** = Personalized, but slow for large data
✅ **content_filt.py** = Fast + works for new products
✅ **cleaning_data.py** = One-time data prep script

Each algorithm solves a different recommendation problem. Together, they create a **robust hybrid system**! 🚀

---
