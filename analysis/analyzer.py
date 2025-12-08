import pandas as pd

class EnergyAnalyzer:

    def compute_basic_stats(self, df: pd.DataFrame):
        if df.empty:
            return None
        return {
            "mean": df["value"].mean(),
            "max": df["value"].max(),
            "min": df["value"].min(),
            "std_dev": df["value"].std()
        }

    def detect_anomalies(self, df: pd.DataFrame, threshold):
        if df.empty:
            return []
        return df[df["value"] > threshold]
