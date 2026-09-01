import pandas as pd
import numpy as np
import os
from app.ml.loader import ModelLoader
from app.utils.config import settings

def run_whatif_simulation(employee_id: int, overrides: dict):
    features_path = os.path.abspath(settings.FEATURES_PATH)
    if not os.path.exists(features_path):
        raise FileNotFoundError(f"Engineered features file not found at {features_path}")
        
    df = pd.read_csv(features_path)
    match = df[df['EmployeeNumber'] == employee_id]
    
    if len(match) == 0:
        return {"error": f"Employee {employee_id} not found."}
        
    emp_data = match.iloc[0].copy()
    pipeline = ModelLoader.get_pipeline()
    
    drop_cols = ['EmployeeNumber', 'Employee ID', 'Attrition', 'Target_Attrition']
    feature_cols = [c for c in df.columns if c not in drop_cols]
    
    base_row = pd.DataFrame([emp_data[feature_cols]])
    base_prob = float(pipeline.predict_proba(base_row)[0, 1])
    
    sim_data = emp_data.copy()
    for k, v in overrides.items():
        if k in sim_data:
            sim_data[k] = v
            
    if 'MonthlyIncome' in overrides or 'YearsAtCompany' in overrides:
        sim_data['Income_Per_Company_Year'] = sim_data['MonthlyIncome'] / (sim_data['YearsAtCompany'] + 1.0)
        
    if 'YearsSinceLastPromotion' in overrides or 'YearsInCurrentRole' in overrides:
        sim_data['Promotion_Delay_Ratio'] = sim_data['YearsSinceLastPromotion'] / (sim_data['YearsInCurrentRole'] + 1.0)
        
    if any(k in overrides for k in ['EnvironmentSatisfaction', 'JobSatisfaction', 'RelationshipSatisfaction', 'WorkLifeBalance']):
        sim_data['Overall_Satisfaction_Index'] = (sim_data['EnvironmentSatisfaction'] + sim_data['JobSatisfaction'] + 
                                                   sim_data['RelationshipSatisfaction'] + sim_data['WorkLifeBalance']) / 4.0

    sim_row = pd.DataFrame([sim_data[feature_cols]])
    new_prob = float(pipeline.predict_proba(sim_row)[0, 1])
    
    delta_prob = new_prob - base_prob
    pct_change = (delta_prob / base_prob) * 100.0 if base_prob > 0 else 0.0
    
    return {
        "EmployeeNumber": employee_id,
        "Baseline_Attrition_Probability": round(base_prob, 4),
        "Simulated_Attrition_Probability": round(new_prob, 4),
        "Risk_Difference": round(delta_prob, 4),
        "Percentage_Risk_Reduction": round(pct_change, 2),
        "Overrides_Applied": overrides
    }
