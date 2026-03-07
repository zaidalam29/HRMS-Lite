"""
Attendance management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime
import logging

from app.api import deps
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceListResponse,
    AttendanceSummary
)
from app.services.attendance_service import AttendanceService
from app.core.exceptions import (
    AttendanceNotFoundError,
    DuplicateAttendanceError,
    EmployeeNotFoundError
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Mark attendance"
)
async def mark_attendance(
    *,
    db: Session = Depends(deps.get_db),
    attendance_in: AttendanceCreate
):
    """
    Mark attendance for an employee.
    
    - **employee_id**: Employee ID
    - **date**: Attendance date (YYYY-MM-DD, cannot be future)
    - **status**: Present or Absent
    - **notes**: Optional notes
    """
    logger.info(f"Marking attendance for employee: {attendance_in.employee_id} on {attendance_in.date}")
    
    try:
        attendance = await AttendanceService.mark_attendance(db, attendance_in)
        logger.info(f"Attendance marked successfully: ID {attendance.id}")
        return attendance
    except EmployeeNotFoundError as e:
        logger.warning(f"Employee not found: {attendance_in.employee_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": str(e),
                "error_code": "EMPLOYEE_NOT_FOUND"
            }
        )
    except DuplicateAttendanceError as e:
        logger.warning(f"Duplicate attendance: {attendance_in.employee_id} on {attendance_in.date}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": str(e),
                "error_code": "DUPLICATE_ATTENDANCE"
            }
        )
    except ValueError as e:
        logger.warning(f"Invalid attendance data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": str(e),
                "error_code": "INVALID_DATA"
            }
        )
    except Exception as e:
        logger.error(f"Error marking attendance: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error marking attendance",
                "error_code": "CREATE_ERROR"
            }
        )

@router.get(
    "/",
    response_model=AttendanceListResponse,
    summary="Get attendance records"
)
async def get_attendance(
    db: Session = Depends(deps.get_db),
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by status (Present/Absent)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return")
):
    """
    Get attendance records with filters and pagination.
    """
    logger.info(f"Fetching attendance records: employee={employee_id}, date_range={start_date}-{end_date}")
    
    try:
        records, total = await AttendanceService.get_attendance_records(
            db,
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            skip=skip,
            limit=limit
        )
        
        logger.info(f"Retrieved {len(records)} attendance records (total: {total})")
        
        return AttendanceListResponse(
            total=total,
            records=records
        )
    except Exception as e:
        logger.error(f"Error fetching attendance: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error fetching attendance records",
                "error_code": "FETCH_ERROR"
            }
        )

@router.get(
    "/employee/{employee_id}",
    response_model=AttendanceListResponse,
    summary="Get employee attendance"
)
async def get_employee_attendance(
    employee_id: str,
    db: Session = Depends(deps.get_db),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get attendance records for a specific employee.
    """
    logger.info(f"Fetching attendance for employee: {employee_id}")
    
    try:
        records, total = await AttendanceService.get_attendance_records(
            db,
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        
        return AttendanceListResponse(
            total=total,
            records=records
        )
    except EmployeeNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": str(e),
                "error_code": "EMPLOYEE_NOT_FOUND"
            }
        )
    except Exception as e:
        logger.error(f"Error fetching employee attendance: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error fetching attendance records",
                "error_code": "FETCH_ERROR"
            }
        )

@router.get(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    summary="Get attendance by ID"
)
async def get_attendance_by_id(
    attendance_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Get a specific attendance record by its ID.
    """
    logger.info(f"Fetching attendance record: {attendance_id}")
    
    try:
        attendance = await AttendanceService.get_attendance_by_id(db, attendance_id)
        return attendance
    except AttendanceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": str(e),
                "error_code": "ATTENDANCE_NOT_FOUND"
            }
        )
    except Exception as e:
        logger.error(f"Error fetching attendance {attendance_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error fetching attendance record",
                "error_code": "FETCH_ERROR"
            }
        )

@router.put(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    summary="Update attendance"
)
async def update_attendance(
    attendance_id: int,
    attendance_in: AttendanceUpdate,
    db: Session = Depends(deps.get_db)
):
    """
    Update an attendance record.
    """
    logger.info(f"Updating attendance record: {attendance_id}")
    
    try:
        attendance = await AttendanceService.update_attendance(
            db, attendance_id, attendance_in
        )
        logger.info(f"Attendance updated successfully: {attendance_id}")
        return attendance
    except AttendanceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": str(e),
                "error_code": "ATTENDANCE_NOT_FOUND"
            }
        )
    except Exception as e:
        logger.error(f"Error updating attendance {attendance_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error updating attendance record",
                "error_code": "UPDATE_ERROR"
            }
        )

@router.delete(
    "/{attendance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete attendance"
)
async def delete_attendance(
    attendance_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Delete an attendance record.
    """
    logger.info(f"Deleting attendance record: {attendance_id}")
    
    try:
        await AttendanceService.delete_attendance(db, attendance_id)
        logger.info(f"Attendance deleted successfully: {attendance_id}")
    except AttendanceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": str(e),
                "error_code": "ATTENDANCE_NOT_FOUND"
            }
        )
    except Exception as e:
        logger.error(f"Error deleting attendance {attendance_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error deleting attendance record",
                "error_code": "DELETE_ERROR"
            }
        )

@router.get(
    "/summary/employee/{employee_id}",
    response_model=AttendanceSummary,
    summary="Get attendance summary"
)
async def get_attendance_summary(
    employee_id: str,
    db: Session = Depends(deps.get_db),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date")
):
    """
    Get attendance summary for an employee.
    """
    logger.info(f"Generating attendance summary for employee: {employee_id}")
    
    try:
        summary = await AttendanceService.get_employee_summary(
            db, employee_id, start_date, end_date
        )
        return summary
    except EmployeeNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": str(e),
                "error_code": "EMPLOYEE_NOT_FOUND"
            }
        )
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error generating attendance summary",
                "error_code": "SUMMARY_ERROR"
            }
        )