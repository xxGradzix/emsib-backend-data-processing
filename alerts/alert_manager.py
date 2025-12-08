import numpy as np

class AlertManager:

    def compute_alerts(self, repo, building_id, high_threshold=50):

        df = repo.get_sensor_data_for_building(building_id)

        if df.empty:
            return {"generated": 0, "reason": "No sensor data"}

        generated = 0

        high_usage = df[df["value"] > high_threshold]

        for _, row in high_usage.iterrows():
            repo.insert_alert(
                device_id=row["deviceId"],
                message=f"High energy usage detected: {row['value']} kWh",
                severity="high"
            )
            generated += 1

        df_sorted = df.sort_values("timestamp")
        df_sorted["diff"] = df_sorted["value"].diff().abs()

        abnormal_jump = df_sorted[df_sorted["diff"] > (df_sorted["value"].std() * 2)]

        for _, row in abnormal_jump.iterrows():
            repo.insert_alert(
                device_id=row["deviceId"],
                message="Sudden abnormal spike detected",
                severity="medium"
            )
            generated += 1

        from datetime import datetime, timedelta

        THRESHOLD_MINUTES = 90

        grouped = df.groupby("deviceId")["timestamp"].max()

        now = datetime.utcnow()

        for device_id, last_ts in grouped.items():
            if (now - last_ts.to_pydatetime()) > timedelta(minutes=THRESHOLD_MINUTES):
                repo.insert_alert(
                    device_id=device_id,
                    message="Device has stopped sending data",
                    severity="high"
                )
                generated += 1

        return {"generated": generated}
