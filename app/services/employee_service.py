"""
Employee business logic with auto-generated employee_id
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Tuple
import logging
import uuid

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.core.exceptions import EmployeeNotFoundError, DuplicateEmployeeError

logger = logging.getLogger(__name__)

class EmployeeService:
    """Service class for employee operations"""
    
    @staticmethod
    async def create_employee(db: Session, employee_data: EmployeeCreate) -> Employee:
        """
        Create a new employee with auto-generated employee_id if not provided
        """
        employee_id = employee_data.employee_id
        if not employee_id:
            employee_id = f"EMP{str(uuid.uuid4())[:8].upper()}"
            logger.info(f"Generated employee_id: {employee_id}")
        
        existing = db.query(Employee).filter(
            Employee.email == employee_data.email
        ).first()
        
        if existing:
            raise DuplicateEmployeeError("email", employee_data.email)
        
        if employee_data.employee_id:
            existing_id = db.query(Employee).filter(
                Employee.employee_id == employee_data.employee_id
            ).first()
            if existing_id:
                raise DuplicateEmployeeError("employee_id", employee_data.employee_id)
        
        employee = Employee(
            employee_id=employee_id,
            full_name=employee_data.full_name,
            email=employee_data.email,
            department=employee_data.department
        )
        
        db.add(employee)
        db.commit()
        db.refresh(employee)
        
        logger.info(f"Employee created: {employee.employee_id} - {employee.full_name}")
        return employee
    
    @staticmethod
    async def get_employees(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        department: Optional[str] = None
    ) -> Tuple[List[Employee], int]:
        """Get all employees with pagination"""
        query = db.query(Employee)
        
        if department:
            query = query.filter(Employee.department == department)
        
        total = query.count()
        employees = query.offset(skip).limit(limit).all()
        
        return employees, total
    
    @staticmethod
    async def get_employee_by_id(db: Session, employee_id: str) -> Employee:
        """Get employee by employee_id"""
        employee = db.query(Employee).filter(
            Employee.employee_id == employee_id
        ).first()
        
        if not employee:
            raise EmployeeNotFoundError(employee_id)
        
        return employee
    
    @staticmethod
    async def update_employee(
        db: Session,
        employee_id: str,
        employee_data: EmployeeUpdate
    ) -> Employee:
        """Update employee information"""
        employee = await EmployeeService.get_employee_by_id(db, employee_id)
        
        if employee_data.email and employee_data.email != employee.email:
            existing = db.query(Employee).filter(
                Employee.email == employee_data.email
            ).first()
            if existing:
                raise DuplicateEmployeeError("email", employee_data.email)
        
        update_data = employee_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(employee, field, value)
        
        db.commit()
        db.refresh(employee)
        
        logger.info(f"Employee updated: {employee_id}")
        return employee
    
    @staticmethod
    async def delete_employee(db: Session, employee_id: str) -> None:
        """Delete employee"""
        employee = await EmployeeService.get_employee_by_id(db, employee_id)
        
        db.delete(employee)
        db.commit()
        
        logger.info(f"Employee deleted: {employee_id}")