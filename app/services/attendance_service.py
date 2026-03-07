"""
Attendance business logic
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case
from typing import List, Optional, Tuple
from datetime import date, datetime
import logging

from app.models.attendance import Attendance, AttendanceStatusEnum
from app.models.employee import Employee
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceSummary
from app.core.exceptions import (
    AttendanceNotFoundError,
    DuplicateAttendanceError,
    EmployeeNotFoundError,
    InvalidDateError
)

logger = logging.getLogger(__name__)

class AttendanceService:
    """Service class for attendance operations"""
    
    @staticmethod
    async def mark_attendance(db: Session, attendance_data: AttendanceCreate) -> Attendance:
        """
        Mark attendance for an employee
        """
        employee = db.query(Employee).filter(
            Employee.employee_id == attendance_data.employee_id
        ).first()
        
        if not employee:
            raise EmployeeNotFoundError(attendance_data.employee_id)
        
        existing = db.query(Attendance).filter(
            and_(
                Attendance.employee_id == attendance_data.employee_id,
                Attendance.date == attendance_data.date
            )
        ).first()
        
        if existing:
            raise DuplicateAttendanceError(
                attendance_data.employee_id,
                attendance_data.date.isoformat()
            )
        
        attendance = Attendance(
            employee_id=attendance_data.employee_id,
            date=attendance_data.date,
            status=attendance_data.status,
            notes=attendance_data.notes
        )
        
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        
        attendance.employee_name = employee.full_name
        
        logger.info(
            f"Attendance marked: {attendance.employee_id} - "
            f"{attendance.date} - {attendance.status}"
        )
        return attendance
    
    @staticmethod
    async def get_attendance_records(
        db: Session,
        employee_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Attendance], int]:
        """
        Get attendance records with filters
        """
        query = db.query(Attendance).join(
            Employee, Attendance.employee_id == Employee.employee_id
        )
        
        if employee_id:
            query = query.filter(Attendance.employee_id == employee_id)
        
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        
        if status:
            query = query.filter(Attendance.status == status)
        
        total = query.count()
        
        records = query.order_by(
            Attendance.date.desc(),
            Attendance.employee_id
        ).offset(skip).limit(limit).all()
        

        for record in records:
            record.employee_name = record.employee.full_name
        
        return records, total
    
    @staticmethod
    async def get_attendance_by_id(db: Session, attendance_id: int) -> Attendance:
        """
        Get attendance record by ID
        """
        attendance = db.query(Attendance).filter(
            Attendance.id == attendance_id
        ).first()
        
        if not attendance:
            raise AttendanceNotFoundError(attendance_id)
        
        attendance.employee_name = attendance.employee.full_name
        return attendance
    
    @staticmethod
    async def update_attendance(
        db: Session,
        attendance_id: int,
        attendance_data: AttendanceUpdate
    ) -> Attendance:
        """
        Update attendance record
        """
        attendance = await AttendanceService.get_attendance_by_id(db, attendance_id)
        
        update_data = attendance_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(attendance, field, value)
        
        db.commit()
        db.refresh(attendance)
        
        attendance.employee_name = attendance.employee.full_name
        logger.info(f"Attendance updated: {attendance_id}")
        return attendance
    
    @staticmethod
    async def delete_attendance(db: Session, attendance_id: int) -> None:
        """
        Delete attendance record
        """
        attendance = await AttendanceService.get_attendance_by_id(db, attendance_id)
        
        db.delete(attendance)
        db.commit()
        
        logger.info(f"Attendance deleted: {attendance_id}")
    
    @staticmethod
    async def get_employee_summary(
        db: Session,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> AttendanceSummary:
        """
        Get attendance summary for an employee
        """
        employee = db.query(Employee).filter(
            Employee.employee_id == employee_id
        ).first()
        
        if not employee:
            raise EmployeeNotFoundError(employee_id)
        
        query = db.query(Attendance).filter(
            Attendance.employee_id == employee_id
        )
        
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        
        total = query.count()
        present = query.filter(Attendance.status == AttendanceStatusEnum.PRESENT).count()
        absent = query.filter(Attendance.status == AttendanceStatusEnum.ABSENT).count()
        
        return AttendanceSummary(
            employee_id=employee_id,
            employee_name=employee.full_name,
            total_present=present,
            total_absent=absent,
            total_records=total
        )