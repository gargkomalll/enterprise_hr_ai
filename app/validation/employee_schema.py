from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal

class EmployeePredictRequest(BaseModel):
    EmployeeNumber: int = Field(..., description="Unique employee identifier")
    Age: int = Field(..., ge=18, le=100, description="Employee age (18-100)")
    BusinessTravel: str = Field(..., description="Business travel category")
    DailyRate: int = Field(800, description="Daily rate (default 800)")
    Department: str = Field(..., description="Department name")
    DistanceFromHome: int = Field(..., ge=1, le=100, description="Distance from home in miles")
    Education: int = Field(..., ge=1, le=5, description="Education level (1-5)")
    EducationField: str = Field(..., description="Field of education")
    EnvironmentSatisfaction: int = Field(..., ge=1, le=4, description="Environment satisfaction (1-4)")
    Gender: str = Field(..., description="Gender")
    HourlyRate: int = Field(..., ge=1, description="Hourly pay rate")
    JobInvolvement: int = Field(..., ge=1, le=4, description="Job involvement score (1-4)")
    JobLevel: int = Field(..., ge=1, le=5, description="Job level (1-5)")
    JobRole: str = Field(..., description="Internal HR job role")
    JobSatisfaction: int = Field(..., ge=1, le=4, description="Job satisfaction score (1-4)")
    MaritalStatus: str = Field(..., description="Marital status")
    MonthlyIncome: int = Field(..., gt=0, description="Monthly income in USD")
    MonthlyRate: int = Field(..., gt=0, description="Monthly rate")
    NumCompaniesWorked: int = Field(..., ge=0, description="Number of prior companies worked")
    OverTime: Literal['Yes', 'No'] = Field(..., description="Overtime status ('Yes' or 'No')")
    PercentSalaryHike: int = Field(..., ge=0, description="Percentage salary hike last year")
    PerformanceRating: int = Field(..., ge=1, le=4, description="Performance rating (1-4)")
    RelationshipSatisfaction: int = Field(..., ge=1, le=4, description="Relationship satisfaction (1-4)")
    StockOptionLevel: int = Field(..., ge=0, le=3, description="Stock option level (0-3)")
    TotalWorkingYears: int = Field(..., ge=0, description="Total working years")
    TrainingTimesLastYear: int = Field(..., ge=0, description="Training sessions last year")
    WorkLifeBalance: int = Field(..., ge=1, le=4, description="Work-life balance score (1-4)")
    YearsAtCompany: int = Field(..., ge=0, description="Years at current company")
    YearsInCurrentRole: int = Field(..., ge=0, description="Years in current role")
    YearsSinceLastPromotion: int = Field(..., ge=0, description="Years since last promotion")
    YearsWithCurrManager: int = Field(..., ge=0, description="Years with current manager")

class WhatIfSimulationRequest(BaseModel):
    EmployeeNumber: int = Field(..., description="Target employee ID")
    Overrides: Dict[str, Any] = Field(..., description="Feature override dict (e.g. {'MonthlyIncome': 6000, 'OverTime': 'No'})")

class ChatRequest(BaseModel):
    message: str = Field(..., description="Natural language HR query string")
    employee_id: Optional[int] = Field(None, description="Optional employee ID context")

class ChatResponse(BaseModel):
    reply: str
    data_summary: Dict[str, Any]
    action_suggestions: list[str]
