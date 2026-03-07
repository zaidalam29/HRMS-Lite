"""
Pydantic schemas for Attendance - Fixed with ConfigDict
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import date
from enum import Enum

class AttendanceStatusEnum(str, Enum):
    PRESENT = "Present"
    ABSENT = "Absent"

class AttendanceBase(BaseModel):
    employee_id: str
    date: date
    status: AttendanceStatusEnum
    notes: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    @field_validator('date')
    @classmethod
    def validate_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError('Attendance date cannot be in the future')
        return v

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatusEnum] = None
    notes: Optional[str] = None

class AttendanceResponse(AttendanceBase):
    id: int
    employee_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class AttendanceListResponse(BaseModel):
    total: int
    records: List[AttendanceResponse]
    
    model_config = ConfigDict(from_attributes=True)

class AttendanceSummary(BaseModel):
    employee_id: str
    employee_name: str
    total_present: int
    total_absent: int
    total_records: int
    
    model_config = ConfigDict(from_attributes=True)