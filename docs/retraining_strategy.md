# Model Retraining Strategy & Protocol

## Overview
This document defines the automated and manual retraining triggers for the Enterprise HR AI attrition prediction model (`models/attrition_pipeline.joblib`).

---

## Retraining Triggers

| Trigger Category | Metric / Condition | Threshold | Protocol Action |
|---|---|---|---|
| **1. Data Drift** | Feature Kolmogorov-Smirnov Test | $p < 0.05$ on 2+ features | Flag for feature drift review; schedule model re-fit. |
| **2. Prediction Drift** | High Risk Ratio Delta | $|\text{Prod High Risk Ratio} - 0.1612| > 0.10$ | Trigger automated retraining pipeline. |
| **3. Model Performance** | F1-Score / Recall Drop | F1 $< 0.45$ or Recall $< 0.70$ on live outcome data | Immediate retraining & challenger model benchmark. |
| **4. Scheduled Cadence** | Elapsed Time | 6 Months elapsed OR 500+ new records | Regular quarterly retraining cadence. |

---

## Retraining Procedure
1. Load newly collected employee survey records (`data/raw/` updates).
2. Execute data cleaning (`03_data_cleaning.ipynb`) & feature engineering (`05_feature_engineering.ipynb`).
3. Re-fit Candidate Models (Logistic Regression, Random Forest, XGBoost).
4. Select winner prioritizing **Recall** and **F1-Score**.
5. Save artifact to `models/v(N+1)/` with updated `metadata.json`.
