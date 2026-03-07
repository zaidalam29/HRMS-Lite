"""
Simple schema exports
"""

from app.schemas.employee import (
    EmployeeBase, EmployeeCreate, EmployeeUpdate,
    EmployeeResponse, EmployeeListResponse, DepartmentEnum
)

from app.schemas.attendance import (
    AttendanceBase, AttendanceCreate, AttendanceUpdate,
    AttendanceResponse, AttendanceListResponse,
    AttendanceSummary, AttendanceStatusEnum
)

__all__ = [
    "EmployeeBase", "EmployeeCreate", "EmployeeUpdate",
    "EmployeeResponse", "EmployeeListResponse", "DepartmentEnum",
    "AttendanceBase", "AttendanceCreate", "AttendanceUpdate",
    "AttendanceResponse", "AttendanceListResponse",
    "AttendanceSummary", "AttendanceStatusEnum"
]