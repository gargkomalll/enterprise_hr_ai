import pandas as pd
import numpy as np
import os
import json
from scipy.stats import ks_2samp, chisquare
from app.utils.config import settings
from app.utils.logger import logger

def check_feature_drift(training_df: pd.DataFrame, production_df: pd.DataFrame):
    """Compares feature distributions using Kolmogorov-Smirnov tests."""
    num_cols = ['Age', 'MonthlyIncome', 'YearsAtCompany', 'Overall_Satisfaction_Index']
    drift_report = {}
    
    for col in num_cols:
        if col in training_df.columns and col in production_df.columns:
            stat, p_val = ks_2samp(training_df[col].dropna(), production_df[col].dropna())
            is_drifted = bool(p_val < 0.05)
            drift_report[col] = {
                "ks_statistic": round(float(stat), 4),
                "p_value": round(float(p_val), 4),
                "drift_detected": is_drifted
            }
            if is_drifted:
                logger.warning(f"⚠️ Feature Drift Detected in '{col}': p-value={p_val:.4f}")
                
    return drift_report

def check_prediction_drift():
    """Compares production prediction log distribution against 16.1% baseline target ratio."""
    log_path = os.path.join(settings.PREDICTIONS_LOG_DIR, "predictions.jsonl")
    if not os.path.exists(log_path):
        return {"status": "No production predictions logged yet."}
        
    records = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line.strip()))
                
    if len(records) < 10:
        return {"status": f"Insufficient records for drift calculation ({len(records)}/10 min)."}
        
    prod_df = pd.DataFrame(records)
    high_risk_ratio = float((prod_df['risk_level'] == 'HIGH').mean())
    baseline_target_ratio = 0.1612
    
    drift_delta = abs(high_risk_ratio - baseline_target_ratio)
    is_drifted = drift_delta > 0.10 # Retrain if high risk ratio shifts by > 10%
    
    return {
        "production_records_count": len(records),
        "production_high_risk_ratio": round(high_risk_ratio, 4),
        "baseline_attrition_ratio": baseline_target_ratio,
        "drift_delta": round(drift_delta, 4),
        "prediction_drift_detected": is_drifted,
        "retraining_recommended": is_drifted
    }

if __name__ == "__main__":
    print("=== Running Data & Model Drift Check ===")
    res = check_prediction_drift()
    print(json.dumps(res, indent=2))
