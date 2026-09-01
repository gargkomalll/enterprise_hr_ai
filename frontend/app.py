import sys
import os

# Prepend project root directory to sys.path so 'app' submodules resolve cleanly
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Ledger — Workforce Intelligence",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# DESIGN TOKENS
# ------------------------------------------------------------
# Concept: a "workforce ledger" — the visual language of a bound
# annual report or personnel register, not a generic SaaS glass
# panel. Deep ink-navy ground, warm paper-toned text, a single
# gold ledger-stamp accent reserved for the signature moments,
# and functional (not decorative) reds/ambers/teals for risk.
# Display serif for headings, a plain-spoken sans for data and
# body copy, tabular figures for anything numeric.
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

:root {
    --ink-bg: #12141b;
    --ink-bg-raised: #181b24;
    --ink-surface: #1d2029;
    --hairline: rgba(201, 178, 140, 0.16);
    --paper: #eae5d8;
    --paper-dim: #9299a6;
    --gold: #c8a133;
    --gold-dim: #8a7126;
    --risk-high: #c1564c;
    --risk-medium: #c99a3c;
    --risk-low: #4d9285;
    --cost-blue: #6f8fb5;
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background-color: var(--ink-bg) !important;
    color: var(--paper);
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Headings carry the institutional-report identity */
h1, h2, h3, .ledger-heading {
    font-family: 'Source Serif 4', serif;
    color: var(--paper);
    letter-spacing: 0.01em;
}

/* Main page title — deliberately oversized, the one signature moment */
[data-testid="stAppViewContainer"] h1,
[data-testid="stMain"] h1 {
    font-weight: 700;
    font-size: 3.4rem;
    line-height: 1.15;
    border-bottom: 1px solid var(--hairline);
    padding-bottom: 0.7rem;
    margin-bottom: 0.4rem;
}

h3 {
    font-weight: 600;
    font-size: 1.15rem;
}

p, span, div, label {
    color: var(--paper);
}

/* -------------------------------------------------------
   Top toolbar (the native Streamlit header strip holding
   the "Deploy" button and the ⋮ menu) — was left on the
   library's default light background; bring it into the
   ledger palette so its controls are actually legible.
-------------------------------------------------------- */
header[data-testid="stHeader"] {
    background-color: var(--ink-bg) !important;
    border-bottom: 1px solid var(--hairline);
}
header[data-testid="stHeader"] * {
    color: var(--paper) !important;
    fill: var(--paper) !important;
}
[data-testid="stToolbar"] button,
.stDeployButton button {
    color: var(--paper) !important;
    background-color: transparent !important;
}
[data-testid="stToolbar"] button:hover {
    background-color: var(--ink-surface) !important;
}
[data-testid="stDecoration"] { background-image: none !important; background-color: var(--gold) !important; }

/* -------------------------------------------------------
   Every text/number input, textarea and dropdown in the
   app — including the chat box — was rendering on the
   framework's default light surface, which made typed
   text (light-on-light) unreadable. Force the ledger
   surface + paper text everywhere a person can type.
-------------------------------------------------------- */
input, textarea,
div[data-baseweb="input"],
div[data-baseweb="textarea"],
div[data-baseweb="base-input"],
div[data-baseweb="select"] > div {
    background-color: var(--ink-surface) !important;
    color: var(--paper) !important;
    border-color: var(--hairline) !important;
    caret-color: var(--paper) !important;
}
input::placeholder, textarea::placeholder {
    color: var(--paper-dim) !important;
    opacity: 1;
}

/* Chat input specifically */
[data-testid="stChatInput"] {
    background-color: var(--ink-surface) !important;
    border: 1px solid var(--hairline) !important;
}
[data-testid="stChatInput"] textarea {
    background-color: transparent !important;
    color: var(--paper) !important;
}
[data-testid="stChatInputSubmitButton"] {
    background-color: var(--gold) !important;
}
[data-testid="stChatInputSubmitButton"] svg { fill: #16181f !important; }

/* Dropdown option lists (selectbox / multiselect popovers) */
ul[data-baseweb="menu"], div[data-baseweb="popover"] {
    background-color: var(--ink-surface) !important;
    border: 1px solid var(--hairline) !important;
}
li[data-baseweb="menu-item"] {
    color: var(--paper) !important;
    background-color: transparent !important;
}
li[data-baseweb="menu-item"]:hover {
    background-color: var(--ink-bg-raised) !important;
}

/* Multiselect selected-value tags — recolored into the
   ledger palette instead of the library's default coral */
span[data-baseweb="tag"] {
    background-color: var(--ink-bg-raised) !important;
    border: 1px solid var(--gold-dim) !important;
    color: var(--paper) !important;
}
span[data-baseweb="tag"] span { color: var(--paper) !important; }
span[data-baseweb="tag"] svg { fill: var(--paper) !important; }

/* Sidebar reads as a ledger spine */
section[data-testid="stSidebar"] {
    background-color: var(--ink-bg-raised);
    border-right: 1px solid var(--hairline);
}
section[data-testid="stSidebar"] h2 {
    font-family: 'Source Serif 4', serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--gold);
    border-bottom: 1px solid var(--hairline);
    padding-bottom: 0.5rem;
}

/* Metric cards: flat ledger sheet with a left rule, not a floating glass tile */
.metric-card {
    background: var(--ink-surface);
    border: 1px solid var(--hairline);
    border-left: 3px solid var(--paper-dim);
    border-radius: 3px;
    padding: 18px 20px;
    margin-bottom: 10px;
}
.metric-card.accent-risk   { border-left-color: var(--risk-high); }
.metric-card.accent-cost   { border-left-color: var(--gold); }
.metric-card.accent-engage { border-left-color: var(--risk-low); }

.metric-title {
    font-size: 0.8rem;
    color: var(--paper-dim);
    font-weight: 500;
    font-family: 'IBM Plex Sans', sans-serif;
}
.metric-value {
    font-family: 'Source Serif 4', serif;
    font-variant-numeric: tabular-nums;
    font-size: 2.1rem;
    font-weight: 600;
    color: var(--paper);
    margin-top: 4px;
}
.metric-badge-high { color: var(--risk-high); }
.metric-badge-cost { color: var(--gold); }

/* Tabs styled as folder tabs in a ledger, underline not pills */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid var(--hairline);
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 500;
    color: var(--paper-dim);
    padding: 10px 18px;
    border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] {
    color: var(--paper);
    border-bottom: 2px solid var(--gold);
    background-color: transparent;
}

/* Buttons: a ledger stamp, not a rounded SaaS pill */
.stButton > button {
    background-color: var(--gold);
    color: #16181f;
    font-weight: 600;
    border: none;
    border-radius: 2px;
    padding: 0.5rem 1.2rem;
}
.stButton > button:hover {
    background-color: var(--gold-dim);
    color: var(--paper);
}

/* Inputs / sliders / selects */
.stSlider [data-baseweb="slider"] > div > div { background: var(--gold); }
div[data-basewef="select"] { color: var(--paper); }
.stSelectbox > div > div, .stMultiSelect > div > div {
    background-color: var(--ink-surface);
    border: 1px solid var(--hairline);
}

hr, .stMarkdown hr { border-color: var(--hairline); }

/* Chat */
.stChatMessage {
    background-color: var(--ink-surface);
    border: 1px solid var(--hairline);
    border-radius: 4px;
}

/* Metric widget (st.metric) used in the simulator */
div[data-testid="stMetric"] {
    background-color: var(--ink-surface);
    border: 1px solid var(--hairline);
    border-left: 3px solid var(--gold);
    border-radius: 3px;
    padding: 12px 16px;
}
div[data-testid="stMetricLabel"] { color: var(--paper-dim); }
div[data-testid="stMetricValue"] { font-family: 'Source Serif 4', serif; color: var(--paper); }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SHARED PLOTLY TEMPLATE — keeps every chart in the same
# ledger palette instead of the stock "plotly_dark" theme
# ============================================================
LEDGER_TEMPLATE = go.layout.Template()
LEDGER_TEMPLATE.layout = go.Layout(
    paper_bgcolor="#12141b",
    plot_bgcolor="#12141b",
    font=dict(family="IBM Plex Sans, sans-serif", color="#eae5d8", size=13),
    title_font=dict(family="Source Serif 4, serif", color="#eae5d8", size=18),
    colorway=["#c8a133", "#6f8fb5", "#4d9285", "#c1564c", "#9299a6"],
    xaxis=dict(gridcolor="rgba(201,178,140,0.12)", zerolinecolor="rgba(201,178,140,0.2)"),
    yaxis=dict(gridcolor="rgba(201,178,140,0.12)", zerolinecolor="rgba(201,178,140,0.2)"),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

RISK_COLOR_MAP = {'HIGH': '#c1564c', 'MEDIUM': '#c99a3c', 'LOW': '#4d9285'}

# Data Loader & Model Pipeline Loader
from app.ml.loader import ModelLoader

DATA_PATH = os.path.join("data", "processed", "employee_intelligence_master.csv")
ORG_SKILLS_PATH = os.path.join("data", "processed", "organization_skill_gaps_rollup.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH) if os.path.exists(DATA_PATH) else pd.DataFrame()
    skills_df = pd.read_csv(ORG_SKILLS_PATH) if os.path.exists(ORG_SKILLS_PATH) else pd.DataFrame()
    return df, skills_df

@st.cache_resource
def get_model_pipeline():
    return ModelLoader.get_pipeline()

df_master, df_skills = load_data()
_pipeline = get_model_pipeline()

# Header
st.title("📖 Ledger — Workforce Intelligence")
st.markdown("Predictive attrition risk, skill gap analytics, financial exposure, and policy simulation for the workforce on record.")

if df_master.empty:
    st.error("Data master file not found. Please ensure data processing pipeline has executed.")
    st.stop()

# Sidebar Navigation & Filters
st.sidebar.header("Register Filters")
selected_dept = st.sidebar.multiselect(
    "Department",
    options=sorted(df_master['Department'].unique().tolist()),
    default=sorted(df_master['Department'].unique().tolist()),
    key="global_dept_filter"
)

selected_risk = st.sidebar.multiselect(
    "Attrition risk tier",
    options=['HIGH', 'MEDIUM', 'LOW'],
    default=['HIGH', 'MEDIUM', 'LOW'],
    key="global_risk_filter"
)

# Apply Filters
filtered_df = df_master[
    (df_master['Department'].isin(selected_dept)) &
    (df_master['Attrition_Risk_Tier'].isin(selected_risk))
]

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Executive Dashboard",
    "Skill Gap & Upskilling",
    "What-If Policy Simulator",
    "Financial Cost Exposure",
    "Employee Drill-Down",
    "HR AI Co-Pilot"
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
            <div class="metric-title">Total workforce</div>
            <div class="metric-value">{total_emp:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card accent-risk">
            <div class="metric-title">High flight risk</div>
            <div class="metric-value metric-badge-high">{high_risk_count} <span style="font-size: 1rem">({high_risk_pct:.1f}%)</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card accent-cost">
            <div class="metric-title">Financial cost exposure</div>
            <div class="metric-value metric-badge-cost">${total_cost:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card accent-engage">
            <div class="metric-title">Avg engagement rating</div>
            <div class="metric-value">{avg_eng:.2f} / 5.0</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Attrition risk tier by department")
        dept_risk = filtered_df.groupby(['Department', 'Attrition_Risk_Tier']).size().reset_index(name='Count')
        fig_dept = px.bar(
            dept_risk,
            x='Department',
            y='Count',
            color='Attrition_Risk_Tier',
            color_discrete_map=RISK_COLOR_MAP,
            barmode='stack',
            template=LEDGER_TEMPLATE
        )
        st.plotly_chart(fig_dept, use_container_width=True)

    with c2:
        st.subheader("Attrition probability vs. monthly income")
        fig_scatter = px.scatter(
            filtered_df,
            x='MonthlyIncome',
            y='Attrition_Probability',
            color='Attrition_Risk_Tier',
            color_discrete_map=RISK_COLOR_MAP,
            hover_data=['EmployeeNumber', 'JobRole', 'YearsAtCompany'],
            template=LEDGER_TEMPLATE
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: SKILL GAP & UPSKILLING
# ---------------------------------------------------------
with tab2:
    st.subheader("Organization-wide skill gap & upskilling paths")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.write("**Top high-severity skill gaps**")
        if not df_skills.empty:
            top_skills = df_skills.head(10)
            fig_skills = px.bar(
                top_skills,
                x='Employees_Lacking_Count',
                y='Missing_Skill_Name',
                orientation='h',
                color='Severity_Tier',
                color_discrete_map=RISK_COLOR_MAP,
                template=LEDGER_TEMPLATE
            )
            fig_skills.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_skills, use_container_width=True)

    with col_b:
        st.write("**Recommended upskilling course enrollments**")
        rec_counts = filtered_df['Recommended_Course_Title'].value_counts().reset_index()
        rec_counts.columns = ['Course Title', 'Target Employee Count']
        fig_recs = px.pie(
            rec_counts,
            values='Target Employee Count',
            names='Course Title',
            hole=0.55,
            template=LEDGER_TEMPLATE
        )
        st.plotly_chart(fig_recs, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: WHAT-IF POLICY SIMULATOR
# ---------------------------------------------------------
with tab3:
    st.subheader("Interactive what-if policy simulator")
    st.markdown("Simulate how policy interventions (compensation hikes, overtime elimination, work-life balance improvements) alter predicted employee flight risk.")

    emp_ids = sorted(df_master['EmployeeNumber'].tolist())
    target_emp_id = st.selectbox("Select employee ID for simulation", options=emp_ids, index=0, key="whatif_emp_select")

    emp_row = df_master[df_master['EmployeeNumber'] == target_emp_id].iloc[0]

    col_sim1, col_sim2 = st.columns(2)

    with col_sim1:
        st.markdown(f"#### Baseline profile — Employee #{target_emp_id}")
        st.write(f"**Department**: {emp_row['Department']} | **Role**: {emp_row['JobRole']}")
        st.write(f"**Current monthly income**: ${emp_row['MonthlyIncome']:,}")
        st.write(f"**Current overtime status**: `{emp_row['OverTime']}`")
        st.write(f"**Current work-life balance rating**: `{emp_row['WorkLifeBalance']} / 4`")
        st.write(f"**Baseline predicted attrition risk**: `{emp_row['Attrition_Probability']*100:.1f}%` ({emp_row['Attrition_Risk_Tier']})")

    with col_sim2:
        st.markdown("#### Hypothetical policy interventions")
        sim_salary_hike = st.slider("Salary increase (%)", min_value=0, max_value=50, value=15, step=5, key="sim_salary_hike_slider")
        sim_overtime = st.selectbox("Eliminate overtime?", options=["No (keep current overtime)", "Yes (remove overtime)"], key="sim_overtime_select")
        sim_wlb = st.slider("Target work-life balance rating", min_value=1, max_value=4, value=4, key="sim_wlb_slider")

        # Calculate simulation
        new_income = emp_row['MonthlyIncome'] * (1 + sim_salary_hike / 100.0)
        new_overtime = "No" if "Yes" in sim_overtime else emp_row['OverTime']

        overrides = {
            "MonthlyIncome": new_income,
            "OverTime": new_overtime,
            "WorkLifeBalance": sim_wlb
        }

        if st.button("Run simulation", key="btn_run_whatif"):
            try:
                from app.services.whatif_service import run_whatif_simulation
                res = run_whatif_simulation(int(target_emp_id), overrides)

                base_p = res['Baseline_Attrition_Probability']
                sim_p = res['Simulated_Attrition_Probability']
                delta = res['Percentage_Risk_Reduction']

                st.success("Simulation executed successfully.")

                sim_col1, sim_col2 = st.columns(2)
                with sim_col1:
                    st.metric("Baseline risk", f"{base_p*100:.1f}%")
                with sim_col2:
                    st.metric("Simulated risk", f"{sim_p*100:.1f}%", delta=f"{delta:.1f}%")

                # Gauge Chart
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=sim_p * 100,
                    title={'text': "Simulated flight risk (%)"},
                    delta={'reference': base_p * 100},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#c8a133"},
                        'bgcolor': "#1d2029",
                        'steps': [
                            {'range': [0, 30], 'color': "#2d4a44"},
                            {'range': [30, 50], 'color': "#4a3d20"},
                            {'range': [50, 100], 'color': "#4a2c28"}
                        ]
                    }
                ))
                fig_gauge.update_layout(template=LEDGER_TEMPLATE, height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)

            except Exception as e:
                st.error(f"Simulation error: {str(e)}")

# ---------------------------------------------------------
# TAB 4: FINANCIAL COST EXPOSURE
# ---------------------------------------------------------
with tab4:
    st.subheader("Financial attrition cost exposure model")

    mult_override = st.slider("Turnover cost multiplier (x annual salary)", min_value=0.5, max_value=3.0, value=1.5, step=0.1, key="cost_mult_slider")

    calc_df = filtered_df.copy()
    calc_df['Annual_Sal'] = calc_df['MonthlyIncome'] * 12
    calc_df['Financial_Exposure'] = calc_df['Annual_Sal'] * mult_override * calc_df['Attrition_Probability']

    total_exp = calc_df['Financial_Exposure'].sum()
    high_exp = calc_df[calc_df['Attrition_Risk_Tier']=='HIGH']['Financial_Exposure'].sum()

    fc1, fc2 = st.columns(2)
    with fc1:
        st.metric("Total projected cost exposure", f"${total_exp:,.2f}")
    with fc2:
        st.metric("High-risk exposure portion", f"${high_exp:,.2f}")

    st.markdown("---")

    cost_by_dept = calc_df.groupby('Department')['Financial_Exposure'].sum().reset_index()
    fig_cost_dept = px.bar(
        cost_by_dept,
        x='Department',
        y='Financial_Exposure',
        color='Financial_Exposure',
        title="Cost exposure by department ($)",
        template=LEDGER_TEMPLATE,
        color_continuous_scale=[[0, "#3a3120"], [0.5, "#8a7126"], [1, "#c8a133"]]
    )
    st.plotly_chart(fig_cost_dept, use_container_width=True)

# ---------------------------------------------------------
# TAB 5: EMPLOYEE DRILL-DOWN
# ---------------------------------------------------------
with tab5:
    st.subheader("Single-employee intelligence profile")

    drill_emp_id = st.selectbox("Select employee for drill-down", options=emp_ids, index=0, key="drill_emp_select")
    drill_row = df_master[df_master['EmployeeNumber'] == drill_emp_id].iloc[0]

    d1, d2 = st.columns(2)

    with d1:
        st.markdown(f"### Profile — Employee #{drill_emp_id}")
        st.write(f"**Department**: {drill_row['Department']}")
        st.write(f"**HR job role**: {drill_row['JobRole']}")
        st.write(f"**Monthly income**: ${drill_row['MonthlyIncome']:,}")
        st.write(f"**Tenure at company**: {drill_row['YearsAtCompany']} years")
        st.write(f"**Years since last promotion**: {drill_row['YearsSinceLastPromotion']} years")
        st.write(f"**Overtime status**: {drill_row['OverTime']}")

    with d2:
        st.markdown("### Risk & upskilling analysis")
        st.markdown(f"**Predicted flight risk**: `{drill_row['Attrition_Probability']*100:.1f}%` (**{drill_row['Attrition_Risk_Tier']}**)")
        st.markdown(f"**Missing skills count**: `{drill_row['Missing_Skills_Count']}` skills")
        st.markdown(f"**Top recommended course path**: `{drill_row['Recommended_Course_Title']}`")

# ---------------------------------------------------------
# TAB 6: HR AI CO-PILOT CHATBOT
# ---------------------------------------------------------
with tab6:
    st.subheader("HR AI co-pilot & natural language intelligence")
    st.markdown("Ask any question about employee attrition risks, department cost exposures, skill gaps, or policy simulations.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi — I'm your workforce intelligence co-pilot. Ask me something like *'Who are the top high flight risk employees?'* or *'What is our financial cost exposure?'*"}
        ]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_prompt = st.chat_input("Ask the co-pilot a question...", key="chat_input_box")
    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            try:
                from app.services.chatbot_service import process_chat_message
                res = process_chat_message(user_prompt)
                reply = res["reply"]
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

                if res.get("action_suggestions"):
                    st.write("**Suggested next actions:**")
                    for sug in res["action_suggestions"]:
                        st.caption(f"→ {sug}")
            except Exception as e:
                st.error(f"Chatbot error: {str(e)}")