import pandas as pd
import numpy as np
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv
import ast


def sanitize_string(text):
    """Re-encodes a string to utf-8, replacing invalid characters."""
    if isinstance(text, str):
        return text.encode('utf-8', 'replace').decode('utf-8')
    return text

def migrate_data():
    """
    Connects to MongoDB, cleans the target collection, and migrates
    cleaned data from a CSV file.
    """
    # --- 1. Load Environment Variables and Connect to MongoDB ---
    load_dotenv()

    mongo_user = os.getenv("MONGO_USER")
    mongo_pass = os.getenv("MONGO_PASS")
    mongo_host = "localhost" # Since we are running this script from our machine

    print("Connecting to MongoDB...")
    # The connection string includes the credentials for authentication
    client = MongoClient(f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:27017/")

    try:
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        print("MongoDB connection successful.")
    except ConnectionFailure:
        print("MongoDB connection failed. Check if Docker container is running.")
        return

    # --- 2. Load Cleaned Data ---
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cleaned_csv_path = os.path.join(project_dir, 'data', 'cleaned_listings.csv')

    print(f"Loading cleaned data from {cleaned_csv_path}")
    try:
        df = pd.read_csv(cleaned_csv_path)
        # Convert date strings back to datetime objects if pandas didn't auto-detect
        for col in ['last_scraped', 'host_since', 'first_review', 'last_review']:
             df[col] = pd.to_datetime(df[col], errors='coerce')
    except FileNotFoundError:
        print(f"Error: Cleaned data file not found at {cleaned_csv_path}")
        client.close()
        return
        
    df = df.where(pd.notnull(df), None)

    # The 'amenities' column might be read as a string from the CSV.
    # We need to re-parse it into a list, just like in the cleaning script.
    def parse_string_list(s):
        try:
            # Check if it's not a NaN/None before trying to eval
            if pd.notna(s):
                return ast.literal_eval(s)
        except (ValueError, SyntaxError):
            pass # Ignore errors
        return [] # Return empty list for NaNs or parsing errors
        
    df['amenities'] = df['amenities'].apply(parse_string_list)

    
    

    # --- 3. Prepare Data for Insertion ---
    print("Transforming data to the target schema...")
    
    # Define the target database and collection
    db = client['rental_db']
    listings_collection = db['listings']
    

    documents_to_insert = []
    for _, row in df.iterrows():
        document = {
            "_id": row['id'],
            # --- APPLY SANITIZE_STRING TO ALL TEXT FIELDS ---
            "listing_url": sanitize_string(row['listing_url']),
            "scraped_at": row['last_scraped'],
            "name": sanitize_string(row['name']),
            "description": sanitize_string(row['description']),
            "property_type": sanitize_string(row['property_type']),
            "room_type": sanitize_string(row['room_type']),
            # --- NO NEED FOR NUMERIC/BOOLEAN/DATE/LISTS ---
            "accommodates": row['accommodates'],
            "bathrooms": row['bathrooms'],
            "bedrooms": row['bedrooms'],
            "beds": row['beds'],
            "amenities": row['amenities'], # This is already a list
            "price": row['price'],
            "minimum_nights": row['minimum_nights'],
            "maximum_nights": row['maximum_nights'],
            "instant_bookable": row['instant_bookable'],
            "host": {
                "id": row['host_id'],
                "name": sanitize_string(row['host_name']),
                "since": row['host_since'],
                "location": sanitize_string(row['host_location']),
                "about": sanitize_string(row['host_about']),
                "is_superhost": row['host_is_superhost'],
                "listings_count": row['host_listings_count'],
                "has_profile_pic": row['host_has_profile_pic'],
                "is_identity_verified": row['host_identity_verified']
            },
            "location": {
                "neighbourhood_cleansed": sanitize_string(row['neighbourhood_cleansed']),
                "coordinates": {
                    "type": "Point",
                    "coordinates": [row['longitude'], row['latitude']] 
                }
            },
            # ... (the rest of the document is fine) ...
            "reviews": { ... },
            "availability": { ... }
        }
        documents_to_insert.append(document)

    # --- 4. Insert Data into MongoDB ---
    if documents_to_insert:
        print("Dropping existing collection to ensure a clean migration...")
        listings_collection.drop()

        print(f"Inserting {len(documents_to_insert)} documents into the 'listings' collection...")
        listings_collection.insert_many(documents_to_insert)
        print("Data migration completed successfully.")
    else:
        print("No documents to insert.")

    client.close()
    print("MongoDB connection closed.")


if __name__ == "__main__":
    migrate_data()