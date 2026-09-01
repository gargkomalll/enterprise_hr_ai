import pandas as pd
import numpy as np
import os
from app.utils.config import settings

def load_master_data():
    master_path = os.path.abspath(settings.DATA_MASTER_PATH)
    if not os.path.exists(master_path):
        raise FileNotFoundError(f"Master data not found at {master_path}")
    return pd.read_csv(master_path)

def get_dashboard_summary():
    df = load_master_data()
    total_emp = len(df)
    high_risk_count = int((df['Attrition_Risk_Tier'] == 'HIGH').sum())
    avg_engagement = round(float(df['Engagement Score'].mean()), 2) if 'Engagement Score' in df.columns else 3.0
    avg_satisfaction = round(float(df['Satisfaction Score'].mean()), 2) if 'Satisfaction Score' in df.columns else 3.0
    
    return {
        "Total_Employees": total_emp,
        "High_Risk_Count": high_risk_count,
        "High_Risk_Percentage": round((high_risk_count / total_emp) * 100.0, 1),
        "Avg_Engagement_Score": avg_engagement,
        "Avg_Satisfaction_Score": avg_satisfaction
    }

def get_attrition_by_department():
    df = load_master_data()
    summary = df.groupby('Department').agg(
        Total_Employees=('EmployeeNumber', 'count'),
        High_Risk_Count=('Attrition_Risk_Tier', lambda x: (x == 'HIGH').sum()),
        Avg_Attrition_Probability=('Attrition_Probability', 'mean')
    ).reset_index()
    summary['Avg_Attrition_Probability'] = summary['Avg_Attrition_Probability'].round(4)
    return summary.to_dict(orient='records')

def get_skill_gaps_summary():
    rollup_path = os.path.abspath(r"data/processed/organization_skill_gaps_rollup.csv")
    if os.path.exists(rollup_path):
        df = pd.read_csv(rollup_path)
        return df.head(15).to_dict(orient='records')
    return []

def get_recommendations_summary():
    df = load_master_data()
    recs = df.groupby('Recommended_Course_Title').agg(
        Enrolled_Employee_Count=('EmployeeNumber', 'count'),
        High_Risk_Target_Count=('Attrition_Risk_Tier', lambda x: (x == 'HIGH').sum())
    ).reset_index().sort_values(by='Enrolled_Employee_Count', ascending=False)
    return recs.to_dict(orient='records')

def get_employee_by_id(employee_id: int):
    df = load_master_data()
    match = df[df['EmployeeNumber'] == employee_id]
    if len(match) == 0:
        return None
    return match.iloc[0].to_dict()

def get_cost_exposure_summary():
    df = load_master_data()
    cost_mult = settings.COST_MULTIPLIER
    df['Annual_Salary'] = df['MonthlyIncome'] * 12
    df['Expected_Cost'] = df['Annual_Salary'] * cost_mult * df['Attrition_Probability']
    
    total_exposure = round(float(df['Expected_Cost'].sum()), 2)
    high_risk_exposure = round(float(df[df['Attrition_Risk_Tier'] == 'HIGH']['Expected_Cost'].sum()), 2)
    
    by_dept = df.groupby('Department').agg(
        Total_Cost_Exposure=('Expected_Cost', 'sum'),
        Employee_Count=('EmployeeNumber', 'count')
    ).reset_index()
    by_dept['Total_Cost_Exposure'] = by_dept['Total_Cost_Exposure'].round(2)
    
    return {
        "Cost_Multiplier_Used": cost_mult,
        "Total_Organization_Cost_Exposure": total_exposure,
        "High_Risk_Cost_Exposure": high_risk_exposure,
        "By_Department": by_dept.to_dict(orient='records')
    }
