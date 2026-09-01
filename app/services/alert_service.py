import os
import json
from datetime import datetime, timezone
from app.utils.config import settings
from app.utils.logger import logger

def trigger_high_risk_alert(employee_id: int, attrition_prob: float, department: str, job_role: str):
    """Sends notification alert when employee is flagged as HIGH risk and logs to data/alerts/."""
    os.makedirs(settings.ALERTS_LOG_DIR, exist_ok=True)
    alert_file = os.path.join(settings.ALERTS_LOG_DIR, "alerts.jsonl")
    
    alert_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "employee_id": employee_id,
        "department": department,
        "job_role": job_role,
        "attrition_probability": round(attrition_prob, 4),
        "risk_level": "HIGH",
        "alert_triggered": True
    }
    
    with open(alert_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(alert_record) + "\n")
        
    logger.warning(f"🚨 ALERT TRIGGERED: High-risk attrition flagged for Employee #{employee_id} ({job_role}, {department}) - Risk: {attrition_prob*100:.1f}%")
    
    if settings.ALERTS_ENABLED and settings.SLACK_WEBHOOK_URL:
        # Optional Slack notification dispatch
        try:
            import requests
            msg = {
                "text": f"🚨 *HIGH Attrition Risk Alert*\n*Employee ID*: {employee_id}\n*Role*: {job_role}\n*Dept*: {department}\n*Risk*: {attrition_prob*100:.1f}%"
            }
            requests.post(settings.SLACK_WEBHOOK_URL, json=msg, timeout=3.0)
            logger.info(f"Dispatched Slack alert for Employee #{employee_id}")
        except Exception as e:
            logger.error(f"Failed to dispatch Slack webhook: {str(e)}")
            
    return alert_record
