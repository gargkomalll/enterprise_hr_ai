import os
from pydantic import BaseModel

class AppSettings(BaseModel):
    APP_NAME: str = "Enterprise HR AI"
    VERSION: str = "1.0.0"
    MODEL_PATH: str = os.getenv("MODEL_PATH", r"models/attrition_pipeline.joblib")
    DATA_MASTER_PATH: str = os.getenv("DATA_MASTER_PATH", r"data/processed/employee_intelligence_master.csv")
    FEATURES_PATH: str = os.getenv("FEATURES_PATH", r"data/processed/features_engineered.csv")
    PREDICTIONS_LOG_DIR: str = os.getenv("PREDICTIONS_LOG_DIR", r"data/predictions")
    ALERTS_LOG_DIR: str = os.getenv("ALERTS_LOG_DIR", r"data/alerts")
    ALERTS_ENABLED: bool = os.getenv("ALERTS_ENABLED", "false").lower() in ("true", "1", "yes")
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
    COST_MULTIPLIER: float = float(os.getenv("COST_MULTIPLIER", "1.5"))

settings = AppSettings()
