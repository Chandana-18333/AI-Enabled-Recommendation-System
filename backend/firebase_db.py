import os
from dotenv import load_dotenv
import pandas as pd
import datetime

load_dotenv()

_firebase_app = None
_auth = None
_db = None

def get_firebase_app():
    global _firebase_app, _auth, _db
    if _firebase_app is None:
        try:
            from pyrebase import initialize_app
            firebase_config = {
                "apiKey": os.getenv("FIREBASE_API_KEY", "placeholder"),
                "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "placeholder"),
                "projectId": os.getenv("FIREBASE_PROJECT_ID", "placeholder"),
                "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", "placeholder"),
                "messagingSenderId": os.getenv("FIREBASE_SENDER_ID", "placeholder"),
                "appId": os.getenv("FIREBASE_APP_ID", "placeholder")
            }
            db_url = os.getenv("FIREBASE_DATABASE_URL", "")
            if db_url:
                firebase_config["databaseURL"] = db_url

            _firebase_app = initialize_app(firebase_config)
            _auth = _firebase_app.auth()
            # Database client for realtime DB
            # Ensure "databaseURL" is properly mapped in your .env
            _db = _firebase_app.database()
        except Exception as e:
            print(f"Firebase Init Error: {e}")
    return _firebase_app

def get_auth():
    if _auth is None:
        get_firebase_app()
    return _auth

def get_db():
    if _db is None:
        get_firebase_app()
    return _db

def log_user_interaction(user_id: int, product_id: str, action_type: str = "view", rating: float = 3.0):
    """
    Log user's view or review history to Firebase Realtime Database.
    We convert the mapped integer user_id.
    """
    db = get_db()
    if not db:
        print("Realtime DB not configured/available.")
        return

    try:
        timestamp = int(datetime.datetime.now().timestamp())
        data = {
            "User's ID": user_id,
            "ProdID": product_id,
            "action": action_type,
            "Rating": rating,
            "timestamp": timestamp
        }
        # Push automatically generates a unique key.
        db.child("user_interactions").child(str(user_id)).push(data)
    except Exception as e:
        print(f"Error logging to Firebase DB: {e}")

def get_user_history_df() -> pd.DataFrame:
    """
    Fetch all interactions across all users, converting to a DataFrame 
    with the required collaborative filtering format:
    User's ID | ProdID | Rating
    """
    db = get_db()
    if not db:
        return pd.DataFrame()
        
    try:
        interactions_node = db.child("user_interactions").get()
        if not interactions_node.val():
            return pd.DataFrame()
            
        rows = []
        for uid, events in interactions_node.val().items():
            if type(events) is dict:
                for event_key, event_data in events.items():
                    rows.append({
                        "User's ID": int(uid),
                        "ProdID": event_data.get("ProdID"),
                        "Rating": event_data.get("Rating", 3.0),
                        "action": event_data.get("action", "unknown")
                    })
        
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"Error reading from Firebase DB: {e}")
        return pd.DataFrame()
