import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import requests

# Page Configuration
st.set_page_config(
    page_title="Enterprise HR AI — Workforce Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphic Dark-Mode CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(4px);
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 5px;
    }
    .metric-badge-high {
        color: #ef4444;
        font-weight: 700;
    }
    .metric-badge-cost {
        color: #38bdf8;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Data Loader
DATA_PATH = os.path.join("data", "processed", "employee_intelligence_master.csv")
ORG_SKILLS_PATH = os.path.join("data", "processed", "organization_skill_gaps_rollup.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH) if os.path.exists(DATA_PATH) else pd.DataFrame()
    skills_df = pd.read_csv(ORG_SKILLS_PATH) if os.path.exists(ORG_SKILLS_PATH) else pd.DataFrame()
    return df, skills_df

df_master, df_skills = load_data()

# Header
st.title("🤖 Enterprise HR AI — Workforce Intelligence Platform")
st.markdown("Predictive Attrition Risk, Skill Gap Analytics, Financial Exposure & Policy Simulation")

if df_master.empty:
    st.error("Data master file not found. Please ensure data processing pipeline has executed.")
    st.stop()

# Sidebar Navigation & Filters
st.sidebar.header("🔍 Global Dashboard Filters")
selected_dept = st.sidebar.multiselect(
    "Select Department(s)",
    options=sorted(df_master['Department'].unique().tolist()),
    default=sorted(df_master['Department'].unique().tolist())
)

selected_risk = st.sidebar.multiselect(
    "Filter by Attrition Risk Tier",
    options=['HIGH', 'MEDIUM', 'LOW'],
    default=['HIGH', 'MEDIUM', 'LOW']
)

# Apply Filters
filtered_df = df_master[
    (df_master['Department'].isin(selected_dept)) &
    (df_master['Attrition_Risk_Tier'].isin(selected_risk))
]

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Dashboard",
    "🎯 Skill Gap & Upskilling",
    "🧪 What-If Policy Simulator",
    "💰 Financial Cost Exposure",
    "👤 Employee Drill-Down"
])

# ---------------------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# ---------------------------------------------------------
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    
    total_emp = len(filtered_df)
    high_risk_count = (filtered_df['Attrition_Risk_Tier'] == 'HIGH').sum()
    high_risk_pct = (high_risk_count / total_emp * 100) if total_emp > 0 else 0.0
    avg_eng = filtered_df['Engagement Score'].mean() if 'Engagement Score' in filtered_df else 3.0
    
    cost_mult = 1.5
    total_cost = (filtered_df['MonthlyIncome'] * 12 * cost_mult * filtered_df['Attrition_Probability']).sum()
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Workforce</div>
            <div class="metric-value">{total_emp:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">High Flight Risk Count</div>
            <div class="metric-value metric-badge-high">{high_risk_count} <span style="font-size: 1rem">({high_risk_pct:.1f}%)</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Financial Cost Exposure</div>
            <div class="metric-value metric-badge-cost">${total_cost:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Engagement Rating</div>
            <div class="metric-value">{avg_eng:.2f} / 5.0</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Attrition Risk Tier Distribution by Department")
        dept_risk = filtered_df.groupby(['Department', 'Attrition_Risk_Tier']).size().reset_index(name='Count')
        fig_dept = px.bar(
            dept_risk,
            x='Department',
            y='Count',
            color='Attrition_Risk_Tier',
            color_discrete_map={'HIGH': '#ef4444', 'MEDIUM': '#f59e0b', 'LOW': '#10b981'},
            barmode='stack',
            template='plotly_dark'
        )
        st.plotly_chart(fig_dept, use_container_width=True)
        
    with c2:
        st.subheader("Attrition Probability vs. Monthly Income")
        fig_scatter = px.scatter(
            filtered_df,
            x='MonthlyIncome',
            y='Attrition_Probability',
            color='Attrition_Risk_Tier',
            color_discrete_map={'HIGH': '#ef4444', 'MEDIUM': '#f59e0b', 'LOW': '#10b981'},
            hover_data=['EmployeeNumber', 'JobRole', 'YearsAtCompany'],
            template='plotly_dark'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: SKILL GAP & UPSKILLING
# ---------------------------------------------------------
with tab2:
    st.subheader("🎯 Organization-Wide Skill Gap & Upskilling Paths")
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.write("### Top High-Severity Skill Gaps")
        if not df_skills.empty:
            top_skills = df_skills.head(10)
            fig_skills = px.bar(
                top_skills,
                x='Employees_Lacking_Count',
                y='Missing_Skill_Name',
                orientation='h',
                color='Severity_Tier',
                color_discrete_map={'HIGH': '#ef4444', 'MEDIUM': '#f59e0b', 'LOW': '#10b981'},
                template='plotly_dark'
            )
            fig_skills.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_skills, use_container_width=True)
            
    with col_b:
        st.write("### Recommended Upskilling Course Enrollments")
        rec_counts = filtered_df['Recommended_Course_Title'].value_counts().reset_index()
        rec_counts.columns = ['Course Title', 'Target Employee Count']
        fig_recs = px.pie(
            rec_counts,
            values='Target Employee Count',
            names='Course Title',
            hole=0.4,
            template='plotly_dark'
        )
        st.plotly_chart(fig_recs, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: WHAT-IF POLICY SIMULATOR
# ---------------------------------------------------------
with tab3:
    st.subheader("🧪 Interactive What-If Policy Simulator")
    st.markdown("Simulate how policy interventions (compensation hikes, overtime elimination, work-life balance improvements) alter predicted employee flight risk.")
    
    emp_ids = sorted(df_master['EmployeeNumber'].tolist())
    target_emp_id = st.selectbox("Select Employee ID for Simulation", options=emp_ids, index=0)
    
    emp_row = df_master[df_master['EmployeeNumber'] == target_emp_id].iloc[0]
    
    col_sim1, col_sim2 = st.columns(2)
    
    with col_sim1:
        st.markdown(f"#### Baseline Profile for Employee #{target_emp_id}")
        st.write(f"**Department**: {emp_row['Department']} | **Role**: {emp_row['JobRole']}")
        st.write(f"**Current Monthly Income**: ${emp_row['MonthlyIncome']:,}")
        st.write(f"**Current OverTime Status**: `{emp_row['OverTime']}`")
        st.write(f"**Current Work-Life Balance Rating**: `{emp_row['WorkLifeBalance']} / 4`")
        st.write(f"**Baseline Predicted Attrition Risk**: `{emp_row['Attrition_Probability']*100:.1f}%` ({emp_row['Attrition_Risk_Tier']})")
        
    with col_sim2:
        st.markdown("#### Hypothetical Policy Interventions")
        sim_salary_hike = st.slider("Salary Increase (%)", min_value=0, max_value=50, value=15, step=5)
        sim_overtime = st.selectbox("Eliminate OverTime?", options=["No (Keep Current OverTime)", "Yes (Remove OverTime)"])
        sim_wlb = st.slider("Target Work-Life Balance Rating", min_value=1, max_value=4, value=4)
        
        # Calculate simulation
        new_income = emp_row['MonthlyIncome'] * (1 + sim_salary_hike / 100.0)
        new_overtime = "No" if "Yes" in sim_overtime else emp_row['OverTime']
        
        overrides = {
            "MonthlyIncome": new_income,
            "OverTime": new_overtime,
            "WorkLifeBalance": sim_wlb
        }
        
        if st.button("🚀 Execute What-If Simulation"):
            try:
                from app.services.whatif_service import run_whatif_simulation
                res = run_whatif_simulation(int(target_emp_id), overrides)
                
                base_p = res['Baseline_Attrition_Probability']
                sim_p = res['Simulated_Attrition_Probability']
                delta = res['Percentage_Risk_Reduction']
                
                st.success("Simulation Executed Successfully!")
                
                sim_col1, sim_col2 = st.columns(2)
                with sim_col1:
                    st.metric("Baseline Risk", f"{base_p*100:.1f}%")
                with sim_col2:
                    st.metric("Simulated Risk", f"{sim_p*100:.1f}%", delta=f"{delta:.1f}%")
                    
                # Gauge Chart
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = sim_p * 100,
                    title = {'text': "Simulated Flight Risk (%)"},
                    delta = {'reference': base_p * 100},
                    gauge = {
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#38bdf8"},
                        'steps': [
                            {'range': [0, 30], 'color': "#10b981"},
                            {'range': [30, 50], 'color': "#f59e0b"},
                            {'range': [50, 100], 'color': "#ef4444"}
                        ]
                    }
                ))
                fig_gauge.update_layout(template='plotly_dark', height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)
                
            except Exception as e:
                st.error(f"Simulation Error: {str(e)}")

# ---------------------------------------------------------
# TAB 4: FINANCIAL COST EXPOSURE
# ---------------------------------------------------------
with tab4:
    st.subheader("💰 Financial Attrition Cost Exposure Model")
    
    mult_override = st.slider("Turnover Cost Multiplier (x Annual Salary)", min_value=0.5, max_value=3.0, value=1.5, step=0.1)
    
    calc_df = filtered_df.copy()
    calc_df['Annual_Sal'] = calc_df['MonthlyIncome'] * 12
    calc_df['Financial_Exposure'] = calc_df['Annual_Sal'] * mult_override * calc_df['Attrition_Probability']
    
    total_exp = calc_df['Financial_Exposure'].sum()
    high_exp = calc_df[calc_df['Attrition_Risk_Tier']=='HIGH']['Financial_Exposure'].sum()
    
    fc1, fc2 = st.columns(2)
    with fc1:
        st.metric("Total Projected Cost Exposure", f"${total_exp:,.2f}")
    with fc2:
        st.metric("High-Risk Exposure Portion", f"${high_exp:,.2f}")
        
    st.markdown("---")
    
    cost_by_dept = calc_df.groupby('Department')['Financial_Exposure'].sum().reset_index()
    fig_cost_dept = px.bar(
        cost_by_dept,
        x='Department',
        y='Financial_Exposure',
        color='Financial_Exposure',
        title="Cost Exposure by Department ($)",
        template='plotly_dark',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_cost_dept, use_container_width=True)

# ---------------------------------------------------------
# TAB 5: EMPLOYEE DRILL-DOWN
# ---------------------------------------------------------
with tab5:
    st.subheader("👤 Single-Employee Intelligence Profile")
    
    drill_emp_id = st.selectbox("Select Employee for Drill-Down", options=emp_ids, index=0)
    drill_row = df_master[df_master['EmployeeNumber'] == drill_emp_id].iloc[0]
    
    d1, d2 = st.columns(2)
    
    with d1:
        st.markdown(f"### Profile: Employee #{drill_emp_id}")
        st.write(f"**Department**: {drill_row['Department']}")
        st.write(f"**HR Job Role**: {drill_row['JobRole']}")
        st.write(f"**Monthly Income**: ${drill_row['MonthlyIncome']:,}")
        st.write(f"**Tenure at Company**: {drill_row['YearsAtCompany']} years")
        st.write(f"**Years Since Last Promotion**: {drill_row['YearsSinceLastPromotion']} years")
        st.write(f"**Overtime Status**: {drill_row['OverTime']}")
        
    with d2:
        st.markdown("### Risk & Upskilling Analysis")
        st.markdown(f"**Predicted Flight Risk**: `{drill_row['Attrition_Probability']*100:.1f}%` (**{drill_row['Attrition_Risk_Tier']}**)")
        st.markdown(f"**Missing Skills Count**: `{drill_row['Missing_Skills_Count']}` skills")
        st.markdown(f"**Top Recommended Course Path**: `{drill_row['Recommended_Course_Title']}`")
