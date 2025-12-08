import matplotlib
matplotlib.use("Agg")  # IMPORTANT: no GUI backend
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd

class GraphGenerator:

    def generate_sensor_graph(self, df, title="Sensor Data", smooth=False):

        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

        plt.figure(figsize=(12, 4))

        if smooth and len(df) >= 5:
            df["smooth"] = df["value"].rolling(window=5, min_periods=1).mean()
            plt.plot(df["timestamp"], df["smooth"], label="Smoothed", color="blue")
        else:
            plt.plot(df["timestamp"], df["value"], label="Value", color="blue")

        plt.title(title)
        plt.xlabel("Timestamp")
        plt.ylabel("Value (kWh)")
        plt.grid(True)
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        img_b64 = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close()
        return img_b64

