from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np

class EnergyForecaster:

    def train_and_forecast(self, df, horizon_hours=24):
        if df.empty:
            return pd.DataFrame()

        df = df.sort_values("timestamp")
        df["t"] = np.arange(len(df))
        X = df[["t"]]
        y = df["value"]

        model = LinearRegression()
        model.fit(X, y)

        future_t = np.arange(len(df), len(df) + horizon_hours)
        predictions = model.predict(future_t.reshape(-1, 1))

        forecast_df = pd.DataFrame({
            "timestamp": pd.date_range(start=df["timestamp"].iloc[-1],
                                       periods=horizon_hours + 1, freq="H")[1:],
            "prediction": predictions
        })

        return forecast_df
