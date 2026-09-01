import logging
import os
import json
from datetime import datetime, timezone
from app.utils.config import settings

# Configure standard Python logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("enterprise_hr_ai")

def log_prediction(employee_id: int, model_version: str, probability: float, risk_level: str):
    """Log individual predictions to data/predictions/ for drift monitoring."""
    os.makedirs(settings.PREDICTIONS_LOG_DIR, exist_ok=True)
    log_file = os.path.join(settings.PREDICTIONS_LOG_DIR, "predictions.jsonl")
    
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "employee_id": employee_id,
        "model_version": model_version,
        "probability": round(probability, 4),
        "risk_level": risk_level
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
        
    logger.info(f"Logged prediction record for Employee #{employee_id}: {risk_level} ({probability*100:.1f}%)")
