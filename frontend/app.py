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
# THEME CONFIGURATION (single fixed dark theme — no toggle)
# ============================================================

# Palette inspired by the reference image, fixed to dark mode only:
# powder blue → warm cream → soft peach → dusty pink → sage, all on a
# deep olive/charcoal base.
bg_color = "#111614"
bg_raised = "#171D1A"
surface_color = "#1E2622"
surface_alt = "#242D28"
hairline_color = "rgba(211, 224, 216, 0.14)"

paper_color = "#E8EEE9"
paper_dim_color = "#AAB7AF"

blue_color = "#79B7C5"
cream_color = "#D9D1BE"
peach_color = "#C99784"
pink_color = "#D88F91"
sage_color = "#9EB29F"
charcoal_color = "#738177"

primary_color = blue_color
gold_color = cream_color

risk_high_color = pink_color
risk_med_color = peach_color
risk_low_color = sage_color

plotly_bg = bg_color
plotly_paper = bg_color
plotly_grid = "rgba(211,224,216,0.10)"

gauge_step_high = "#4A3032"
gauge_step_med = "#49392F"
gauge_step_low = "#2E4037"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

:root {{
    --app-bg: {bg_color};
    --app-raised: {bg_raised};
    --surface: {surface_color};
    --surface-alt: {surface_alt};
    --line: {hairline_color};

    --text: {paper_color};
    --text-dim: {paper_dim_color};

    --blue: {blue_color};
    --cream: {cream_color};
    --peach: {peach_color};
    --pink: {pink_color};
    --sage: {sage_color};
    --charcoal: {charcoal_color};

    --risk-high: {risk_high_color};
    --risk-medium: {risk_med_color};
    --risk-low: {risk_low_color};
}}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {{
    background: var(--app-bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}}

[data-testid="stMainBlockContainer"] {{
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}}

h1, h2, h3, .ledger-heading {{
    font-family: 'Playfair Display', serif;
    color: var(--text) !important;
    letter-spacing: -0.015em;
}}

[data-testid="stAppViewContainer"] h1,
[data-testid="stMain"] h1 {{
    font-weight: 700;
    font-size: 3.05rem;
    line-height: 1.12;
    border-bottom: 0;
    padding-bottom: 0;
    margin-bottom: 0.25rem;
}}

[data-testid="stMain"] h1::after {{
    content: "";
    display: block;
    width: 76px;
    height: 5px;
    margin-top: 13px;
    border-radius: 999px;
    background: linear-gradient(
        90deg,
        var(--blue) 0 25%,
        var(--peach) 25% 50%,
        var(--pink) 50% 75%,
        var(--sage) 75% 100%
    );
}}

h3 {{
    font-weight: 600;
    font-size: 1.18rem;
}}

p, span, div, label {{
    color: var(--text) !important;
}}

[data-testid="stMarkdownContainer"] p {{
    color: var(--text-dim) !important;
}}

header[data-testid="stHeader"] {{
    background: var(--app-bg) !important;
    border-bottom: 1px solid var(--line);
}}

header[data-testid="stHeader"] * {{
    color: var(--text) !important;
    fill: var(--text) !important;
}}

[data-testid="stToolbar"] button,
.stDeployButton button {{
    color: var(--text) !important;
    background: transparent !important;
}}

[data-testid="stToolbar"] button:hover {{
    background: var(--surface) !important;
}}

[data-testid="stDecoration"] {{
    background-image: none !important;
    background-color: var(--blue) !important;
}}

input, textarea,
div[data-baseweb="input"],
div[data-baseweb="textarea"],
div[data-baseweb="base-input"],
div[data-baseweb="select"] > div {{
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    caret-color: var(--text) !important;
}}

input:focus, textarea:focus {{
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 2px rgba(153,203,216,0.18) !important;
}}

input::placeholder, textarea::placeholder {{
    color: var(--text-dim) !important;
    opacity: 1;
}}

[data-testid="stChatInput"] {{
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 16px !important;
}}

[data-testid="stChatInput"] textarea {{
    background: transparent !important;
    color: var(--text) !important;
}}

[data-testid="stChatInputSubmitButton"] {{
    background: var(--blue) !important;
    border-radius: 12px !important;
}}

[data-testid="stChatInputSubmitButton"] svg {{
    fill: #24302C !important;
}}

/* ---- Dropdown / multiselect popovers (select, multiselect) ----
   These render in a portal at the end of <body>, so we target every
   BaseWeb attribute regardless of the wrapping element (ul/div/li)
   and force a max-height + scroll so long option lists never get
   clipped the way they were before. */
[data-baseweb="popover"] {{
    z-index: 9999 !important;
}}

[data-baseweb="popover"] [data-baseweb="menu"],
[data-baseweb="popover"] ul[role="listbox"],
[data-baseweb="popover"] div[role="listbox"] {{
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    box-shadow: 0 12px 32px rgba(0,0,0,0.18) !important;
    max-height: 280px !important;
    overflow-y: auto !important;
    padding: 4px !important;
}}

[data-baseweb="popover"] li,
[data-baseweb="popover"] [role="option"],
[data-baseweb="menu-item"] {{
    background: transparent !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    padding: 8px 10px !important;
}}

[data-baseweb="popover"] li:hover,
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="menu-item"]:hover,
[data-baseweb="popover"] [aria-selected="true"] {{
    background: var(--surface-alt) !important;
    color: var(--text) !important;
}}

/* Scrollbar so a long options list is obviously scrollable, not cut off */
[data-baseweb="popover"] *::-webkit-scrollbar {{
    width: 8px;
}}
[data-baseweb="popover"] *::-webkit-scrollbar-thumb {{
    background: var(--line) !important;
    border-radius: 8px;
}}
[data-baseweb="popover"] *::-webkit-scrollbar-track {{
    background: transparent;
}}

/* ---- Multiselect chips (Department / Risk tier pills) ----
   Recolored from bright red into an elegant soft pastel sage/slate pill */
div[data-testid="stMultiSelect"] span[data-baseweb="tag"],
div[data-testid="stMultiSelect"] div[data-baseweb="tag"],
section[data-testid="stSidebar"] [data-baseweb="tag"],
[data-baseweb="tag"],
span[data-baseweb="tag"],
div[data-baseweb="tag"],
.stMultiSelect [data-baseweb="tag"],
[data-baseweb="tag"][style] {{
    background-color: #273630 !important;
    background: #273630 !important;
    border: 1px solid rgba(158, 178, 159, 0.4) !important;
    color: #E8EEE9 !important;
    border-radius: 999px !important;
    box-shadow: none !important;
}}

[data-baseweb="tag"] *,
span[data-baseweb="tag"] *,
div[data-baseweb="tag"] * {{
    background-color: transparent !important;
    background: transparent !important;
    color: #E8EEE9 !important;
    fill: #E8EEE9 !important;
}}

[data-baseweb="tag"] svg,
span[data-baseweb="tag"] svg {{
    fill: #AAB7AF !important;
}}

[data-baseweb="tag"]:hover {{
    background-color: #30423B !important;
    border-color: var(--blue) !important;
}}

section[data-testid="stSidebar"] {{
    background:
        linear-gradient(
            180deg,
            var(--surface) 0%,
            var(--surface-alt) 100%
        ) !important;
    border-right: 1px solid var(--line);
}}

section[data-testid="stSidebar"] h2 {{
    font-family: 'Playfair Display', serif;
    font-size: 1.12rem;
    font-weight: 600;
    color: var(--text) !important;
    border-bottom: 0;
    padding-bottom: 0.5rem;
}}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    border-radius: 10px;
}}

.metric-card {{
    position: relative;
    overflow: hidden;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 21px 22px;
    margin-bottom: 10px;
    box-shadow: 0 8px 24px rgba(40,48,44,0.06);
}}

.metric-card::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    background: var(--blue);
}}

.metric-card.accent-risk::before {{ background: var(--pink); }}
.metric-card.accent-cost::before {{ background: var(--peach); }}
.metric-card.accent-engage::before {{ background: var(--sage); }}

.metric-title {{
    font-size: 0.78rem;
    color: var(--text-dim) !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-top: 3px;
}}

.metric-value {{
    font-family: 'Playfair Display', serif;
    font-variant-numeric: tabular-nums;
    font-size: 2.15rem;
    font-weight: 600;
    color: var(--text) !important;
    margin-top: 5px;
}}

.metric-badge-high {{ color: var(--risk-high) !important; }}
.metric-badge-cost {{ color: var(--peach) !important; }}

.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    border-bottom: 1px solid var(--line);
    background: transparent;
}}

.stTabs [data-baseweb="tab"] {{
    background: transparent;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    color: var(--text-dim) !important;
    padding: 11px 16px;
    border-bottom: 3px solid transparent;
}}

.stTabs [aria-selected="true"] {{
    color: var(--text) !important;
    border-bottom: 3px solid var(--blue);
    background: transparent;
}}

.stButton > button {{
    background: #0C0F0D !important;
    color: #F4F1E8 !important;
    font-weight: 700;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    padding: 0.62rem 1.25rem;
    transition: all 0.2s ease;
}}

.stButton > button:hover {{
    background: #1B211D !important;
    color: #F4F1E8 !important;
    border-color: var(--blue) !important;
    transform: translateY(-1px);
}}

.stChatMessage {{
    background: var(--surface) !important;
    border: 1px solid var(--line);
    border-radius: 16px;
    box-shadow: 0 5px 18px rgba(40,48,44,0.04);
}}

div[data-testid="stMetric"] {{
    background: var(--surface) !important;
    border: 1px solid var(--line);
    border-top: 4px solid var(--blue);
    border-left: 0;
    border-radius: 15px;
    padding: 13px 16px;
}}

div[data-testid="stMetricLabel"] {{
    color: var(--text-dim) !important;
}}

div[data-testid="stMetricValue"] {{
    font-family: 'Playfair Display', serif;
    color: var(--text) !important;
}}

[data-testid="stExpander"] {{
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 14px !important;
}}

hr {{
    border-color: var(--line) !important;
}}

.stSlider [data-baseweb="slider"] div {{
    background-color: var(--blue);
}}

.stSelectbox label, .stMultiSelect label, .stRadio label {{
    font-weight: 600 !important;
}}

</style>
""", unsafe_allow_html=True)

LEDGER_TEMPLATE = go.layout.Template()
LEDGER_TEMPLATE.layout = go.Layout(
    paper_bgcolor=plotly_paper,
    plot_bgcolor=plotly_bg,
    font=dict(family="IBM Plex Sans, sans-serif", color=paper_color, size=13),
    title_font=dict(family="Source Serif 4, serif", color=paper_color, size=18),
    colorway=[blue_color, peach_color, pink_color, sage_color, charcoal_color, cream_color],
    xaxis=dict(gridcolor=plotly_grid, zerolinecolor=hairline_color),
    yaxis=dict(gridcolor=plotly_grid, zerolinecolor=hairline_color),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

RISK_COLOR_MAP = {'HIGH': risk_high_color, 'MEDIUM': risk_med_color, 'LOW': risk_low_color}

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
                        'bar': {'color': primary_color},
                        'bgcolor': surface_alt,
                        'steps': [
                            {'range': [0, 30], 'color': gauge_step_low},
                            {'range': [30, 50], 'color': gauge_step_med},
                            {'range': [50, 100], 'color': gauge_step_high}
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
        color_continuous_scale=[[0, sage_color], [0.5, peach_color], [1, blue_color]]
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