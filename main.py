# File: main.py
import pandas as pd
import requests
import datetime
import os
from io import StringIO
from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.utils import RepositoryNotFoundError, EntryNotFoundError

# --- CONFIGURATION ---
REPO_ID = "Shivansh1969/pi-sensor-log"
FILENAME = "weather_data.csv"
# SECURELY GET TOKEN FROM GITHUB SECRETS
HF_TOKEN = os.getenv("HF_TOKEN") 
CITY_LAT = 12.9716  # Bangalore Latitude
CITY_LON = 77.5946  # Bangalore Longitude
TIMEZONE = "Asia/Kolkata"

def get_weather_data(start_date, end_date):
    """Fetches historical weather data from Open-Meteo."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": CITY_LAT,
        "longitude": CITY_LON,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["relative_humidity_2m_mean", "surface_pressure_mean"],
        "timezone": TIMEZONE
    }
    
    print(f"Fetching weather data from {start_date} to {end_date}...")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        dates = data['daily']['time']
        humidity = data['daily']['relative_humidity_2m_mean']
        pressure = data['daily']['surface_pressure_mean']
        
        # --- EDITED: Columns renamed to match Dashboard requirements ---
        df = pd.DataFrame({
            "Date_Time": dates,               # Was "Date"
            "Humidity_Percent": humidity,     # Was "average humidity(%)"
            "Pressure_hPa": pressure          # Was "average pressure(hPa)"
        })
        return df
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return pd.DataFrame()

def main():
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN not found. Make sure it is set in GitHub Secrets.")

    api = HfApi(token=HF_TOKEN)
    
    # Calculate dates
    today = datetime.datetime.now().date()
    yesterday = today - datetime.timedelta(days=1)
    
    # Check if dataset exists on Hugging Face
    file_exists = False
    try:
        print("Checking for existing dataset on Hugging Face...")
        downloaded_path = hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            repo_type="dataset",
            token=HF_TOKEN
        )
        existing_df = pd.read_csv(downloaded_path)
        file_exists = True
        print("Existing dataset found.")

        # --- NEW: Rename old columns if they exist in the downloaded file ---
        # This prevents errors if the old file has "Date" but we need "Date_Time"
        rename_map = {
            "Date": "Date_Time",
            "average humidity(%)": "Humidity_Percent",
            "average pressure(hPa)": "Pressure_hPa"
        }
        existing_df.rename(columns=rename_map, inplace=True)

    except (RepositoryNotFoundError, EntryNotFoundError):
        print("No existing dataset found. Initializing new dataset.")
        existing_df = pd.DataFrame()
    except Exception as e:
        print(f"Error accessing Hugging Face: {e}")
        return

    # --- LOGIC BRANCHING ---
    if not file_exists:
        # First Run: Backfill 30 days
        start_date = yesterday - datetime.timedelta(days=30)
        final_df = get_weather_data(start_date, yesterday)
        if final_df.empty:
            print("No data fetched. Aborting.")
            return
        print("Generated 30-day backfill data.")
        
    else:
        # Daily Update: Fetch only Yesterday
        # --- EDITED: Check for 'Date_Time' instead of 'Date' ---
        if 'Date_Time' in existing_df.columns and str(yesterday) in existing_df['Date_Time'].values:
            print(f"Data for {yesterday} already exists. Skipping update.")
            return

        new_data = get_weather_data(yesterday, yesterday)
        if new_data.empty:
            print("No new data fetched. Aborting.")
            return
            
        final_df = pd.concat([existing_df, new_data], ignore_index=True)
        print(f"Appended data for {yesterday}.")

    # --- UPLOAD TO HUGGING FACE ---
    print("Uploading updated dataset to Hugging Face...")
    csv_buffer = StringIO()
    final_df.to_csv(csv_buffer, index=False)
    
    try:
        api.upload_file(
            path_or_fileobj=csv_buffer.getvalue().encode(),
            path_in_repo=FILENAME,
            repo_id=REPO_ID,
            repo_type="dataset",
            commit_message=f"Update weather data: {yesterday}"
        )
        print("Upload successful!")
    except Exception as e:
        print(f"Upload failed: {e}")

if __name__ == "__main__":
    main()
