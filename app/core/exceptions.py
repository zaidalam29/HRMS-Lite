"""
Custom exception classes for HRMS application
"""

from typing import Optional, Dict, Any

class HRMSException(Exception):
    """Base exception for all HRMS exceptions"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)

class EmployeeNotFoundError(HRMSException):
    """Raised when employee is not found"""
    
    def __init__(self, employee_id: str):
        super().__init__(
            message=f"Employee with ID '{employee_id}' not found",
            status_code=404,
            error_code="EMPLOYEE_NOT_FOUND",
            details={"employee_id": employee_id}
        )

class DuplicateEmployeeError(HRMSException):
    """Raised when employee with same ID or email already exists"""
    
    def __init__(self, field: str, value: str):
        super().__init__(
            message=f"Employee with {field} '{value}' already exists",
            status_code=409,
            error_code="DUPLICATE_EMPLOYEE",
            details={field: value}
        )

class AttendanceNotFoundError(HRMSException):
    """Raised when attendance record is not found"""
    
    def __init__(self, attendance_id: int):
        super().__init__(
            message=f"Attendance record with ID '{attendance_id}' not found",
            status_code=404,
            error_code="ATTENDANCE_NOT_FOUND",
            details={"attendance_id": attendance_id}
        )

class DuplicateAttendanceError(HRMSException):
    """Raised when attendance already marked for date"""
    
    def __init__(self, employee_id: str, date: str):
        super().__init__(
            message=f"Attendance already marked for employee '{employee_id}' on {date}",
            status_code=409,
            error_code="DUPLICATE_ATTENDANCE",
            details={"employee_id": employee_id, "date": date}
        )

class InvalidDateError(HRMSException):
    """Raised when date format is invalid"""
    
    def __init__(self, date_str: str):
        super().__init__(
            message=f"Invalid date format: '{date_str}'. Use YYYY-MM-DD",
            status_code=400,
            error_code="INVALID_DATE",
            details={"date": date_str}
        )

class DatabaseError(HRMSException):
    """Raised for database operation errors"""
    
    def __init__(self, operation: str, detail: str = ""):
        super().__init__(
            message=f"Database error during {operation}",
            status_code=500,
            error_code="DATABASE_ERROR",
            details={"operation": operation, "detail": detail}
        )