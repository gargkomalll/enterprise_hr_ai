import pandas as pd
import numpy as np
from app.ml.loader import ModelLoader
from app.utils.logger import logger, log_prediction
from app.services.alert_service import trigger_high_risk_alert

def predict_single_employee_attrition(employee_data: dict):
    pipeline = ModelLoader.get_pipeline()
    
    df = pd.DataFrame([employee_data])
    if 'DailyRate' not in df.columns or pd.isnull(df['DailyRate'].iloc[0]):
        df['DailyRate'] = 800
    
    # Feature engineering for incoming single record
    df['Income_Per_Company_Year'] = df['MonthlyIncome'] / (df['YearsAtCompany'] + 1.0)
    df['Promotion_Delay_Ratio'] = df['YearsSinceLastPromotion'] / (df['YearsInCurrentRole'] + 1.0)
    df['Experience_Ratio'] = df['YearsAtCompany'] / (df['TotalWorkingYears'] + 1.0)
    df['Overall_Satisfaction_Index'] = (df['EnvironmentSatisfaction'] + df['JobSatisfaction'] + 
                                         df['RelationshipSatisfaction'] + df['WorkLifeBalance']) / 4.0

    # Ensure engagement fields are populated
    for col in ['Engagement Score', 'Satisfaction Score', 'Work-Life Balance Score', 'Current Employee Rating']:
        if col not in df.columns:
            df[col] = 3.0
            
    proba = float(pipeline.predict_proba(df)[0, 1])
    
    if proba >= 0.50:
        risk_level = "HIGH"
    elif proba >= 0.30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
        
    emp_id = int(employee_data.get('EmployeeNumber', 0))
    
    # Prediction logging
    log_prediction(emp_id, "v1.0.0", proba, risk_level)
    
    # Alerting service trigger for high-risk predictions
    if risk_level == "HIGH":
        trigger_high_risk_alert(
            emp_id, proba, 
            employee_data.get('Department', 'Unknown'), 
            employee_data.get('JobRole', 'Unknown')
        )
        
    return {
        "EmployeeNumber": emp_id,
        "Attrition_Probability": round(proba, 4),
        "Attrition_Risk_Tier": risk_level,
        "Model_Version": "v1.0.0"
    }
