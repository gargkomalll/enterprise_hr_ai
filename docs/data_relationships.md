# Data Relationships & Key Mapping Matrix

This document defines the join logic, join keys, relationship cardinality, and entity justifications for all table pairs across the Enterprise HR AI system.

## Summary Join Matrix

| Left Table | Right Table | Join Key(s) | Relationship Type | Entity Justification & Handling |
|---|---|---|---|---|
| `employee_attrition_processed` | `engagement_processed` | `EmployeeNumber` == `Employee ID` | **1:1** (Optional Left Join) | Both tables record employee-level records. 731 direct overlapping IDs. Missing records filled via department/role medians. |
| `employee_attrition_processed` | `occupation_master` | `JobRole` $ightarrow$ `O*NET-SOC Code` | **Many:1** | Multiple employees share an HR job role, mapped to master O*NET SOC occupation codes. |
| `occupation_master` | `essential_skills_processed` | `O*NET-SOC Code` | **1:Many** | One occupation code defines multiple required essential role skills and importance scores (`Scale ID == 'IM'`). |
| `occupation_master` | `software_skills_processed` | `O*NET-SOC Code` | **1:Many** | One occupation code defines multiple required software tools (`Normalized_Tool_Name`). |

---

## Entity & Key Verification Details

### 1. `employee_attrition_processed` $\leftrightarrow$ `engagement_processed`
- **Key Alignment**: `EmployeeNumber` (int) in Attrition matches `Employee ID` (int) in Engagement.
- **Cardinality**: 1:1 per matched employee ID.
- **Join Rule**: `LEFT JOIN` on `EmployeeNumber == Employee ID`. Employees without matching engagement surveys receive imputated median scores calculated by `Department` and `JobRole`.

### 2. `employee_attrition_processed` $\leftrightarrow$ `occupation_master`
- **Key Alignment**: Explicit dictionary mapping in `app/services/role_service.py` connects 9 HR JobRoles to standard O*NET SOC codes:
  - `Sales Executive` $ightarrow$ `41-4012.00`
  - `Research Scientist` $ightarrow$ `19-1029.01`
  - `Laboratory Technician` $ightarrow$ `29-2012.00`
  - `Manufacturing Director` $ightarrow$ `11-1021.00`
  - `Healthcare Representative` $ightarrow$ `41-4011.00`
  - `Manager` $ightarrow$ `11-1021.00`
  - `Sales Representative` $ightarrow$ `41-4012.00`
  - `Research Director` $ightarrow$ `11-9121.00`
  - `Human Resources` $ightarrow$ `13-1071.00`
- **Cardinality**: Many:1.
