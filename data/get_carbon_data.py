import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_carbon_data(start_date, end_date):
    url = f"https://api.carbonintensity.org.uk/intensity/{start_date}/{end_date}"
    response = requests.get(url)
    data = response.json()['data']
    
    df = pd.DataFrame([{
        'timestamp': entry['from'],
        'carbon_gCO2_per_kWh': entry['intensity']['actual']
    } for entry in data if entry['intensity']['actual'] is not None])
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

if __name__ == "__main__":
    end = datetime.utcnow().date()
    start = end - timedelta(days=7)
    
    df = fetch_carbon_data(start, end)
    df.to_csv("data/carbon_intensity.csv", index=False)
    print("✅ Carbon data saved to data/carbon_intensity.csv")