"""
Attendance database model
"""

from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base

class AttendanceStatusEnum(str, enum.Enum):
    PRESENT = "Present" 
    ABSENT = "Absent"

class Attendance(Base):
    """Attendance model"""
    
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(
        String,
        ForeignKey("employees.employee_id", ondelete="CASCADE"),
        nullable=False
    )
    date = Column(Date, nullable=False)
    status = Column(Enum(AttendanceStatusEnum), nullable=False)
    notes = Column(String, nullable=True)
    
    employee = relationship("Employee", back_populates="attendance_records")
    
    __table_args__ = (
        UniqueConstraint(
            'employee_id',
            'date',
            name='unique_attendance_per_day'
        ),
    )
    
    def __repr__(self):
        return f"<Attendance {self.employee_id} - {self.date}: {self.status}>"