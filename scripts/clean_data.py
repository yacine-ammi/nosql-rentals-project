import pandas as pd
import numpy as np
import os
import ast

def clean_and_transform_listings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and transforms the raw listings data.
    """
    print("Starting data cleaning and transformation...")
    
    # Work on a copy to avoid SettingWithCopyWarning
    df_clean = df.copy()

    # --- Column Selection ---
    relevant_columns = [
        'id','listing_url', 'last_scraped', 'name', 'description', 'property_type', 'room_type',
        'accommodates', 'bathrooms_text', 'bedrooms', 'beds', 'amenities', 'price',
        'minimum_nights', 'maximum_nights', 'instant_bookable', 'host_id', 'host_name',
        'host_since', 'host_location', 'host_about', 'host_is_superhost',
        'host_listings_count', 'host_has_profile_pic', 'host_identity_verified',
        'neighbourhood_cleansed', 'latitude', 'longitude', 'number_of_reviews',
        'review_scores_rating', 'review_scores_accuracy', 'review_scores_cleanliness',
        'review_scores_checkin', 'review_scores_communication', 'review_scores_location',
        'review_scores_value', 'first_review', 'last_review', 'has_availability'
    ]
    df_clean = df_clean[relevant_columns]

    # --- Data Type Conversion and Cleaning ---

    # Price: Convert from string '$1,234.56' to float 1234.56
    df_clean['price'] = df_clean['price'].str.replace(r'[$,]', '', regex=True).astype(float)

    # Boolean columns: Convert 't'/'f' to True/False
    bool_map = {'t': True, 'f': False}
    for col in ['instant_bookable', 'host_is_superhost', 'host_has_profile_pic', 'host_identity_verified', 'has_availability']:
        df_clean[col] = df_clean[col].map(bool_map).astype(bool)

    # Date columns: Convert to datetime objects, coercing errors to NaT (Not a Time)
    date_cols = ['last_scraped', 'host_since', 'first_review', 'last_review']
    for col in date_cols:
        df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')

    # Numeric columns: Fill missing values (NaN)
    # For review scores, a 0 is a reasonable default for missing scores.
    review_score_cols = [
        'review_scores_rating', 'review_scores_accuracy', 'review_scores_cleanliness',
        'review_scores_checkin', 'review_scores_communication', 'review_scores_location',
        'review_scores_value'
    ]
    df_clean[review_score_cols] = df_clean[review_score_cols].fillna(0)

    # For bedrooms/beds, a listing must have at least one. Let's fill NaNs with 1.
    df_clean['bedrooms'] = df_clean['bedrooms'].fillna(1)
    df_clean['beds'] = df_clean['beds'].fillna(1)
    
    # Text columns: Fill missing values with an empty string
    text_cols = ['description', 'host_about', 'host_location']
    df_clean[text_cols] = df_clean[text_cols].fillna('')

    # Special handling for 'bathrooms_text'
    # Extracts the first number found in the string. If no number, it becomes NaN.
    df_clean['bathrooms'] = df_clean['bathrooms_text'].str.extract(r'(\d+\.?\d*)').astype(float)
    df_clean['bathrooms'] = df_clean['bathrooms'].fillna(0) # Fill any remaining NaNs
    df_clean = df_clean.drop(columns=['bathrooms_text']) # Drop the original text column

    # --- Parsing Stringified Lists ---
    # The 'amenities' column is a string that looks like a list.
    # We use ast.literal_eval to safely parse it into an actual list.
    def parse_string_list(s):
        try:
            return ast.literal_eval(s)
        except (ValueError, SyntaxError):
            return [] # Return an empty list if parsing fails
    
    df_clean['amenities'] = df_clean['amenities'].apply(parse_string_list)
    
    print("Data cleaning and transformation complete.")
    return df_clean

def main():
    # Define project paths
    # This makes the script runnable from the root project directory.
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_dir, 'data')
    input_csv_path = os.path.join(data_dir, 'listings_Paris.csv')
    output_csv_path = os.path.join(data_dir, 'cleaned_listings.csv')

    # --- Load ---
    print(f"Loading data from {input_csv_path}")
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"Error: The file was not found at {input_csv_path}")
        return

    # --- Clean ---
    try:
        print("Cleaning and transforming data...")  
        df_cleaned = clean_and_transform_listings(df)
        print("Data cleaning and transformation completed successfully.")
    except Exception as e:
        print(f"Error during cleaning: {e}")
        return
    

    # --- Save ---
    print(f"Saving cleaned data to {output_csv_path}")
    df_cleaned.to_csv(output_csv_path, index=False)
    print("Script finished successfully.")


if __name__ == "__main__":
    main()