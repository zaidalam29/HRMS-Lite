"""
Employee database model with auto-generated employee_id
"""

from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

from app.core.database import Base

class DepartmentEnum(str, enum.Enum):
    ENGINEERING = "Engineering"
    MARKETING = "Marketing"
    SALES = "Sales"
    HUMAN_RESOURCES = "Human Resources"
    FINANCE = "Finance"
    OPERATIONS = "Operations"

class Employee(Base):
    """Employee model with auto-generated employee_id"""
    
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False, default=lambda: f"EMP{str(uuid.uuid4())[:8].upper()}")
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    department = Column(Enum(DepartmentEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    attendance_records = relationship(
        "Attendance",
        back_populates="employee",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    def __repr__(self):
        return f"<Employee {self.employee_id}: {self.full_name}>"