"""
Employee management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.api import deps
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListResponse
)
from app.services.employee_service import EmployeeService
from app.core.exceptions import EmployeeNotFoundError, DuplicateEmployeeError

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new employee"
)
async def create_employee(
    *,
    db: Session = Depends(deps.get_db),
    employee_in: EmployeeCreate
):
    """
    Create a new employee.
    
    - **employee_id**: Optional - If not provided, will be auto-generated
    - **full_name**: Employee's full name
    - **email**: Valid email address
    - **department**: Employee's department
    """
    log_msg = f"Creating new employee"
    if employee_in.employee_id:
        log_msg += f" with ID: {employee_in.employee_id}"
    else:
        log_msg += " (ID will be auto-generated)"
    logger.info(log_msg)
    
    try:
        employee = await EmployeeService.create_employee(db, employee_in)
        logger.info(f"Employee created successfully: {employee.employee_id}")
        return employee
    except DuplicateEmployeeError as e:
        logger.warning(f"Duplicate employee attempt")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": str(e),
                "error_code": "DUPLICATE_EMPLOYEE"
            }
        )
    except Exception as e:
        logger.error(f"Error creating employee: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error creating employee",
                "error_code": "CREATE_ERROR"
            }
        )
@router.get(
    "/",
    response_model=EmployeeListResponse,
    summary="Get all employees"
)
async def get_employees(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    department: Optional[str] = Query(None, description="Filter by department")
):
    """
    Get all employees with pagination.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **department**: Optional department filter
    """
    logger.info(f"Fetching employees: skip={skip}, limit={limit}, department={department}")
    
    try:
        employees, total = await EmployeeService.get_employees(
            db, skip=skip, limit=limit, department=department
        )
        
        logger.info(f"Retrieved {len(employees)} employees (total: {total})")
        
        return EmployeeListResponse(
            total=total,
            employees=employees
        )
    except Exception as e:
        logger.error(f"Error fetching employees: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error fetching employees",
                "error_code": "FETCH_ERROR"
            }
        )

@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Get employee by ID"
)
async def get_employee(
    employee_id: str,
    db: Session = Depends(deps.get_db)
):
    """
    Get a specific employee by their employee ID.
    """
    logger.info(f"Fetching employee: {employee_id}")
    
    try:
        employee = await EmployeeService.get_employee_by_id(db, employee_id)
        logger.info(f"Employee found: {employee_id}")
        return employee
    except EmployeeNotFoundError as e:
        logger.warning(f"Employee not found: {employee_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": str(e),
                "error_code": "EMPLOYEE_NOT_FOUND"
            }
        )
    except Exception as e:
        logger.error(f"Error fetching employee {employee_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error fetching employee",
                "error_code": "FETCH_ERROR"
            }
        )

@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Update employee"
)
async def update_employee(
    employee_id: str,
    employee_in: EmployeeUpdate,
    db: Session = Depends(deps.get_db)
):
    """
    Update an employee's information.
    """
    logger.info(f"Updating employee: {employee_id}")
    
    try:
        employee = await EmployeeService.update_employee(
            db, employee_id, employee_in
        )
        logger.info(f"Employee updated successfully: {employee_id}")
        return employee
    except EmployeeNotFoundError as e:
        logger.warning(f"Employee not found for update: {employee_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": str(e),
                "error_code": "EMPLOYEE_NOT_FOUND"
            }
        )
    except Exception as e:
        logger.error(f"Error updating employee {employee_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error updating employee",
                "error_code": "UPDATE_ERROR"
            }
        )

@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete employee"
)
async def delete_employee(
    employee_id: str,
    db: Session = Depends(deps.get_db)
):
    """
    Delete an employee and all their attendance records.
    """
    logger.info(f"Deleting employee: {employee_id}")
    
    try:
        await EmployeeService.delete_employee(db, employee_id)
        logger.info(f"Employee deleted successfully: {employee_id}")
    except EmployeeNotFoundError as e:
        logger.warning(f"Employee not found for deletion: {employee_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": str(e),
                "error_code": "EMPLOYEE_NOT_FOUND"
            }
        )
    except Exception as e:
        logger.error(f"Error deleting employee {employee_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error deleting employee",
                "error_code": "DELETE_ERROR"
            }
        )