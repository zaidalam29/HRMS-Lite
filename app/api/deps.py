"""
Common dependencies for API routes
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.employee import Employee

logger = logging.getLogger(__name__)

__all__ = ["get_db", "get_employee_by_id"]

def get_employee_by_id(
    employee_id: str,
    db: Session = Depends(get_db)
) -> Employee:
    """
    Get employee by ID or raise 404
    """
    employee = db.query(Employee).filter(
        Employee.employee_id == employee_id
    ).first()
    
    if not employee:
        logger.warning(f"Employee not found: {employee_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Employee with ID {employee_id} not found",
                "error_code": "EMPLOYEE_NOT_FOUND"
            }
        )
    
    return employee