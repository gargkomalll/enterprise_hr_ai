from fastapi import APIRouter, HTTPException, status
from app.validation.employee_schema import EmployeePredictRequest, WhatIfSimulationRequest
from app.services.prediction_service import predict_single_employee_attrition
from app.services.analytics_service import (
    get_dashboard_summary,
    get_attrition_by_department,
    get_skill_gaps_summary,
    get_recommendations_summary,
    get_employee_by_id,
    get_cost_exposure_summary
)
from app.services.whatif_service import run_whatif_simulation

router = APIRouter()

@router.post("/predict/attrition", status_code=status.HTTP_200_OK)
def predict_attrition(payload: EmployeePredictRequest):
    try:
        result = predict_single_employee_attrition(payload.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/dashboard/summary")
def dashboard_summary():
    return get_dashboard_summary()

@router.get("/dashboard/attrition-by-department")
def attrition_by_department():
    return get_attrition_by_department()

@router.get("/dashboard/skill-gaps")
def skill_gaps():
    return get_skill_gaps_summary()

@router.get("/dashboard/recommendations")
def recommendations():
    return get_recommendations_summary()

@router.get("/employees/{employee_id}")
def employee_detail(employee_id: int):
    emp = get_employee_by_id(employee_id)
    if emp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee {employee_id} not found")
    return emp

@router.post("/simulate/whatif")
def simulate_whatif(payload: WhatIfSimulationRequest):
    result = run_whatif_simulation(payload.EmployeeNumber, payload.Overrides)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return result

@router.get("/dashboard/cost-exposure")
def cost_exposure():
    return get_cost_exposure_summary()
