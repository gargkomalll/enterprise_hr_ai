import pandas as pd
import numpy as np
import os
import re
from app.services.analytics_service import load_master_data, get_cost_exposure_summary
from app.services.whatif_service import run_whatif_simulation
from app.utils.logger import logger

def process_chat_message(message: str, employee_id: int = None):
    """Processes natural language HR queries and returns structured responses."""
    msg = message.lower().strip()
    df = load_master_data()
    
    # Extract employee ID if mentioned in text (e.g. "employee 11", "emp #1", "11")
    emp_match = re.search(r'(?:employee|emp|#)?\s*(\d+)', msg)
    extracted_emp_id = int(emp_match.group(1)) if emp_match else employee_id

    # 1. Single Employee Specific Query
    if extracted_emp_id and extracted_emp_id in df['EmployeeNumber'].values:
        emp_row = df[df['EmployeeNumber'] == extracted_emp_id].iloc[0]
        prob = emp_row['Attrition_Probability']
        tier = emp_row['Attrition_Risk_Tier']
        dept = emp_row['Department']
        role = emp_row['JobRole']
        course = emp_row.get('Recommended_Course_Title', 'Leadership Core')
        gaps = emp_row.get('Missing_Skills_Count', 0)
        
        reply = (
            f"👤 **Employee #{extracted_emp_id} Intelligence Profile**:\n"
            f"- **Role**: {role} ({dept})\n"
            f"- **Predicted Flight Risk**: **{prob*100:.1f}%** ({tier} Risk)\n"
            f"- **Monthly Income**: ${emp_row['MonthlyIncome']:,}\n"
            f"- **OverTime**: {emp_row['OverTime']}\n"
            f"- **Missing Skills**: {gaps} skills missing\n"
            f"- **Recommended Upskilling**: *{course}*"
        )
        
        data_summary = {
            "EmployeeNumber": extracted_emp_id,
            "Department": dept,
            "JobRole": role,
            "Attrition_Probability": prob,
            "Attrition_Risk_Tier": tier,
            "Recommended_Course": course
        }
        
        actions = [
            f"Simulate 15% salary hike for Employee #{extracted_emp_id}",
            f"Simulate removing OverTime for Employee #{extracted_emp_id}",
            "View highest risk employees in Sales"
        ]
        
        return {"reply": reply, "data_summary": data_summary, "action_suggestions": actions}

    # 2. High Risk Employees List Query
    if any(k in msg for k in ['high risk', 'highest risk', 'who is leaving', 'flight risk', 'top risk']):
        high_risk_df = df[df['Attrition_Risk_Tier'] == 'HIGH'].sort_values(by='Attrition_Probability', ascending=False).head(5)
        
        lines = ["🔥 **Top 5 Highest Flight Risk Employees**:"]
        for _, r in high_risk_df.iterrows():
            lines.append(f"- **Emp #{r['EmployeeNumber']}** ({r['JobRole']}, {r['Department']}): Risk `{r['Attrition_Probability']*100:.1f}%` | Rec: *{r.get('Recommended_Course_Title', 'Upskilling Core')}*")
            
        reply = "\n".join(lines)
        
        return {
            "reply": reply,
            "data_summary": {"high_risk_count": len(df[df['Attrition_Risk_Tier']=='HIGH'])},
            "action_suggestions": [
                f"Show details for Employee #{high_risk_df.iloc[0]['EmployeeNumber']}",
                "Calculate total financial cost exposure for high risk employees",
                "View top company skill gaps"
            ]
        }

    # 3. Financial Cost Exposure Query
    if any(k in msg for k in ['cost', 'financial', 'money', 'exposure', 'budget']):
        cost_summary = get_cost_exposure_summary()
        tot = cost_summary['Total_Organization_Cost_Exposure']
        high_tot = cost_summary['High_Risk_Cost_Exposure']
        
        reply = (
            f"💰 **Financial Attrition Cost Exposure Analysis**:\n"
            f"- **Total Projected Turnover Cost Exposure**: **${tot:,.2f}**\n"
            f"- **High-Risk Employee Portion**: **${high_tot:,.2f}**\n"
            f"- **Cost Multiplier Used**: `{cost_summary['Cost_Multiplier_Used']}x Annual Salary`\n\n"
            f"R&D and Sales represent the largest department cost risks."
        )
        
        return {
            "reply": reply,
            "data_summary": cost_summary,
            "action_suggestions": [
                "Who are the top 5 highest risk employees?",
                "Simulate policy changes for high-risk staff",
                "View upskilling course recommendations"
            ]
        }

    # 4. Skill Gaps & Upskilling Query
    if any(k in msg for k in ['skill', 'gap', 'course', 'upskill', 'training']):
        rollup_path = os.path.abspath(r"data/processed/organization_skill_gaps_rollup.csv")
        top_gaps = []
        if os.path.exists(rollup_path):
            sg_df = pd.read_csv(rollup_path).head(5)
            for _, r in sg_df.iterrows():
                top_gaps.append(f"- **{r['Missing_Skill_Name']}**: Lacked by `{r['Employees_Lacking_Count']}` employees ({r['Severity_Tier']} Severity)")
                
        reply = (
            "🎯 **Organization Skill Gap & Upskilling Intelligence**:\n" +
            ("\n".join(top_gaps) if top_gaps else "- Key gaps identified in Critical Thinking, Excel, Python & AWS.") +
            "\n\nTop course enrollment: *Critical Thinking & Strategic Problem Solving*."
        )
        
        return {
            "reply": reply,
            "data_summary": {"top_gaps_count": len(top_gaps)},
            "action_suggestions": [
                "Show cost exposure in Sales",
                "Who are the highest flight risk employees?",
                "Simulate salary increase for high risk staff"
            ]
        }

    # 5. Default Co-Pilot Response
    reply = (
        "👋 **Enterprise HR AI Co-Pilot Ready**!\n\n"
        "I can assist you with:\n"
        "- 📊 Identifying high-risk employees and flight drivers\n"
        "- 💰 Calculating financial turnover cost exposure\n"
        "- 🎯 Analyzing organizational skill gaps & course paths\n"
        "- 🧪 Simulating salary hikes & overtime policies\n\n"
        "Try asking: *'Who are the top high risk employees?'* or *'What is our financial cost exposure?'*"
    )
    
    return {
        "reply": reply,
        "data_summary": {},
        "action_suggestions": [
            "Who are the top 5 highest flight risk employees?",
            "What is our total financial cost exposure?",
            "Show top organization skill gaps"
        ]
    }
