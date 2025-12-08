from pymongo import MongoClient
from bson import ObjectId
import pandas as pd
from datetime import datetime

class MongoRepository:
    def __init__(self, uri="mongodb+srv://Developer:Developer@seenergysystem.7wul3ai.mongodb.net/",
                 db_name="energy_management"):

        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def save_energy_report(self, building_id, report):
        """
        Save an energy report into the EnergyReports collection.
        PeriodStart & PeriodEnd MUST be datetime objects, summary must be dict of floats.
        """
        entry = {
            "buildingId": ObjectId(building_id),
            "periodStart": report["periodStart"],
            "periodEnd": report["periodEnd"],
            "summary": {k: float(v) for k, v in report["summary"].items()},
            "generatedBy": report.get("generatedBy", "system")
        }

        self.db["EnergyReports"].insert_one(entry)
        return entry
    def get_sensor_data_for_device(self, device_id, limit=5000):
        cursor = self.db["SensorData"].find(
            {"deviceId": ObjectId(device_id)}
        ).sort("timestamp", -1).limit(limit)

        df = pd.DataFrame(list(cursor))
        if df.empty:
            return df

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    def get_sensor_data_for_building(self, building_id, limit=5000):
        devices = list(self.db["Devices"].find({"buildingId": ObjectId(building_id)}))
        device_ids = [d["_id"] for d in devices]

        cursor = self.db["SensorData"].find(
            {"deviceId": {"$in": device_ids}}
        ).sort("timestamp", -1).limit(limit)

        df = pd.DataFrame(list(cursor))
        if df.empty:
            return df

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    def insert_alert(self, device_id, message, severity="medium"):
        alert_doc = {
            "deviceId": ObjectId(device_id),
            "type": "auto",
            "message": message,
            "timestamp": datetime.utcnow(),
            "severity": severity,
            "resolved": False
        }
        self.db["Alerts"].insert_one(alert_doc)

    def get_alerts_for_building(self, building_id):
        devices = list(self.db["Devices"].find({"buildingId": ObjectId(building_id)}))
        device_ids = [d["_id"] for d in devices]
        return list(self.db["Alerts"].find({"deviceId": {"$in": device_ids}}))
