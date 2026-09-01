import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.prediction_service import predict_single_employee_attrition

client = TestClient(app)

# Sample valid employee payload
VALID_PAYLOAD = {
    "EmployeeNumber": 9999,
    "Age": 35,
    "BusinessTravel": "Travel_Rarely",
    "Department": "Sales",
    "DistanceFromHome": 10,
    "Education": 3,
    "EducationField": "Life Sciences",
    "EnvironmentSatisfaction": 2,
    "Gender": "Male",
    "HourlyRate": 60,
    "JobInvolvement": 3,
    "JobLevel": 2,
    "JobRole": "Sales Executive",
    "JobSatisfaction": 2,
    "MaritalStatus": "Single",
    "MonthlyIncome": 5000,
    "MonthlyRate": 15000,
    "NumCompaniesWorked": 2,
    "OverTime": "Yes",
    "PercentSalaryHike": 12,
    "PerformanceRating": 3,
    "RelationshipSatisfaction": 3,
    "StockOptionLevel": 0,
    "TotalWorkingYears": 10,
    "TrainingTimesLastYear": 2,
    "WorkLifeBalance": 2,
    "YearsAtCompany": 4,
    "YearsInCurrentRole": 2,
    "YearsSinceLastPromotion": 1,
    "YearsWithCurrManager": 2
}

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_dashboard_summary_endpoint():
    response = client.get("/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "Total_Employees" in data
    assert data["Total_Employees"] == 1470

def test_attrition_by_department_endpoint():
    response = client.get("/dashboard/attrition-by-department")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_predict_attrition_valid_payload():
    response = client.post("/predict/attrition", json=VALID_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert "Attrition_Probability" in data
    assert 0.0 <= data["Attrition_Probability"] <= 1.0
    assert data["Attrition_Risk_Tier"] in ["HIGH", "MEDIUM", "LOW"]

def test_predict_attrition_invalid_age():
    invalid_payload = VALID_PAYLOAD.copy()
    invalid_payload["Age"] = 15 # Invalid age < 18
    response = client.post("/predict/attrition", json=invalid_payload)
    assert response.status_code == 422 # Validation error

def test_predict_attrition_invalid_overtime():
    invalid_payload = VALID_PAYLOAD.copy()
    invalid_payload["OverTime"] = "Maybe" # Invalid enum
    response = client.post("/predict/attrition", json=invalid_payload)
    assert response.status_code == 422

def test_simulate_whatif_endpoint():
    payload = {
        "EmployeeNumber": 11,
        "Overrides": {"OverTime": "No", "WorkLifeBalance": 4}
    }
    response = client.post("/simulate/whatif", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Simulated_Attrition_Probability" in data
    assert data["Simulated_Attrition_Probability"] <= data["Baseline_Attrition_Probability"]

def test_cost_exposure_endpoint():
    response = client.get("/dashboard/cost-exposure")
    assert response.status_code == 200
    data = response.json()
    assert "Total_Organization_Cost_Exposure" in data
    assert data["Total_Organization_Cost_Exposure"] > 0

def test_chatbot_endpoint():
    payload = {"message": "Who are the highest flight risk employees?"}
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "action_suggestions" in data
    assert len(data["action_suggestions"]) > 0

def test_rag_evaluation_metrics():
    from app.monitoring.rag_eval import evaluate_retrieval_system
    results = evaluate_retrieval_system(k=3)
    assert results["Evaluated_Metric_K"] == 3
    assert results["Mean_Recall_at_K"] >= 0.80
    assert results["Mean_Reciprocal_Rank_MRR"] >= 0.80
