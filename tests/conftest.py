"""
Pytest fixtures for testing - Fixed with correct enum values
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator, Dict
from datetime import date, datetime, timedelta
import time

from app.main import app
from app.core.database import Base, get_db
from app.models.employee import Employee, DepartmentEnum
from app.models.attendance import Attendance, AttendanceStatusEnum

TEST_DATABASE_URL = "postgresql://postgres:@localhost:5432/hrms_test_db"

engine = create_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test database tables once per test session"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_employee_data() -> Dict:
    """Sample employee data with correct department value"""
    unique_id = int(time.time() * 1000)
    return {
        "full_name": "John Doe",
        "email": f"john.doe.{unique_id}@example.com",
        "department": "Engineering" 
    }

@pytest.fixture(scope="function")
def test_employee_with_id_data() -> Dict:
    """Sample employee data with custom ID and correct department"""
    unique_id = int(time.time() * 1000)
    return {
        "employee_id": f"EMP{unique_id}",
        "full_name": "Jane Smith",
        "email": f"jane.smith.{unique_id}@example.com",
        "department": "Marketing"  
    }

@pytest.fixture(scope="function")
def test_attendance_data(test_employee_with_id_data) -> Dict:
    """Sample attendance data with correct status"""
    return {
        "employee_id": test_employee_with_id_data["employee_id"],
        "date": str(date.today()),
        "status": "Present",
        "notes": "On time"
    }

@pytest.fixture(scope="function")
def create_test_employee(db):
    """Create a test employee in database"""
    unique_id = int(time.time() * 1000)
    employee_id = f"EMP{unique_id}"
    email = f"test.{unique_id}@example.com"
    
    employee = Employee(
        employee_id=employee_id,
        full_name="Test User",
        email=email,
        department=DepartmentEnum.ENGINEERING  
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

@pytest.fixture(scope="function")
def create_test_attendance(db, create_test_employee):
    """Create a test attendance record in database"""
    attendance = Attendance(
        employee_id=create_test_employee.employee_id,
        date=date.today(),
        status=AttendanceStatusEnum.PRESENT,  
        notes="Test attendance"
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance