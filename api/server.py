from fastapi import FastAPI
from data_access.mongo_repository import MongoRepository
from analysis.analyzer import EnergyAnalyzer
from analysis.reporter import ReportGenerator
from forecasting.forecaster import EnergyForecaster
from alerts.alert_manager import AlertManager
from pydantic import BaseModel
from visualization.graph_generator import GraphGenerator
import pandas as pd
from datetime import datetime

app = FastAPI(title="EMSIB API with MongoDB")

repo = MongoRepository()
analyzer = EnergyAnalyzer()
reporter = ReportGenerator()
forecaster = EnergyForecaster()
alerts = AlertManager()
graph_gen = GraphGenerator()

@app.get("/health")
def health():
    return {"status": "OK", "db": repo.db.name}

@app.get("/report/{building_id}")
def generate_report(building_id: str):

    df = repo.get_sensor_data_for_building(building_id)

    if df.empty:
        return {"error": "No sensor data available for this building"}

    stats = analyzer.compute_basic_stats(df)

    if stats is None:
        return {"error": "Could not compute statistics"}

    period_start_dt = df["timestamp"].min()
    period_end_dt = df["timestamp"].max()

    response_report = {
        "periodStart": period_start_dt.isoformat(),
        "periodEnd": period_end_dt.isoformat(),
        "summary": {k: float(v) for k, v in stats.items()},
        "generatedBy": "system"
    }

    db_report = {
        "periodStart": period_start_dt,
        "periodEnd": period_end_dt,
        "summary": stats,
        "generatedBy": "system"
    }

    repo.save_energy_report(building_id, db_report)

    return response_report

class ForecastRequest(BaseModel):
    horizon_hours: int = 24

@app.post("/forecast/{building_id}")
def generate_forecast(building_id: str, req: ForecastRequest):
    df = repo.get_sensor_data_for_building(building_id)

    forecast_df = forecaster.train_and_forecast(df, req.horizon_hours)
    return {"forecast": forecast_df.to_dict(orient="records")}

def serialize_alert(alert):
    alert["_id"] = str(alert["_id"])
    alert["deviceId"] = str(alert["deviceId"])
    alert["timestamp"] = str(alert["timestamp"])
    return alert

@app.get("/alerts/{building_id}")
def get_alerts(building_id: str):
    alerts = repo.get_alerts_for_building(building_id)
    return [serialize_alert(a) for a in alerts]

@app.post("/alerts/compute/{building_id}")
def compute_alerts(building_id: str):
    result = alerts.compute_alerts(repo, building_id)
    return result

@app.get("/graph/sensor/{building_id}")
def get_sensor_graph(building_id: str, deviceId: str = None, smooth: bool = False):

    if deviceId:
        df = repo.get_sensor_data_for_device(deviceId)
    else:
        df = repo.get_sensor_data_for_building(building_id)

    if df.empty:
        return {"error": "No sensor data available"}

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["timestamp", "value"])
    df = df.sort_values("timestamp")

    if len(df) < 5:
        smooth = False

    b64 = graph_gen.generate_sensor_graph(df, smooth=smooth)

    return {"image": f"data:image/png;base64,{b64}"}
