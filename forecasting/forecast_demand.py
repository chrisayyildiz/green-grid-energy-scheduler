import pandas as pd
from prophet import Prophet
from datetime import timedelta

def load_data():
    df = pd.read_csv("data/simulated_energy_demand.csv", parse_dates=["timestamp"])
    df = df.rename(columns={"timestamp": "ds", "simulated_demand_kWh": "y"})
    return df

def train_and_forecast(df, periods=7*96):  # 96 x 15min = 1 day
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True
    )
    model.fit(df)

    future = model.make_future_dataframe(periods=periods, freq='15min')
    forecast = model.predict(future)

    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

if __name__ == "__main__":
    df = load_data()
    forecast = train_and_forecast(df)
    forecast.to_csv("data/forecasted_energy_demand.csv", index=False)
    print("✅ Forecast saved to data/forecasted_energy_demand.csv")