"""
Pydantic schemas for Employee - Fixed with ConfigDict
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DepartmentEnum(str, Enum):
    ENGINEERING = "Engineering"
    MARKETING = "Marketing"
    SALES = "Sales"
    HUMAN_RESOURCES = "Human Resources"
    FINANCE = "Finance"
    OPERATIONS = "Operations"

class EmployeeBase(BaseModel):
    full_name: str
    email: EmailStr
    department: DepartmentEnum

class EmployeeCreate(EmployeeBase):
    employee_id: Optional[str] = None

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[DepartmentEnum] = None

class EmployeeResponse(EmployeeBase):
    id: int
    employee_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class EmployeeListResponse(BaseModel):
    total: int
    employees: List[EmployeeResponse]
    
    model_config = ConfigDict(from_attributes=True)