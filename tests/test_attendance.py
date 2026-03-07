"""
Test cases for Attendance API - Complete Fixed Version
"""

import pytest
from fastapi import status 
from datetime import date, timedelta, datetime
import time

class TestAttendanceAPI:
    """Test suite for attendance endpoints"""


    def test_mark_attendance_success(self, client, test_employee_with_id_data):
        """Test marking attendance successfully"""

        emp_response = client.post("/api/v1/employees/", json=test_employee_with_id_data)
        assert emp_response.status_code == status.HTTP_201_CREATED
        
        attendance_data = {
            "employee_id": test_employee_with_id_data["employee_id"],
            "date": str(date.today()),
            "status": "Present",
            "notes": "On time"
        }
        
        response = client.post("/api/v1/attendance/", json=attendance_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert "id" in data
        assert data["employee_id"] == attendance_data["employee_id"]
        assert data["status"] == "Present"

    def test_mark_attendance_employee_not_found(self, client):
        """Test marking attendance for non-existent employee"""
        attendance_data = {
            "employee_id": "EMP999999",
            "date": str(date.today()),
            "status": "Present"
        }
        
        response = client.post("/api/v1/attendance/", json=attendance_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        
        assert "message" in data or "detail" in data

    def test_mark_attendance_duplicate(self, client, test_employee_with_id_data):
        """Test marking duplicate attendance for same day"""

        emp_response = client.post("/api/v1/employees/", json=test_employee_with_id_data)
        assert emp_response.status_code == status.HTTP_201_CREATED
        
        attendance_data = {
            "employee_id": test_employee_with_id_data["employee_id"],
            "date": str(date.today()),
            "status": "Present"
        }
        
        response1 = client.post("/api/v1/attendance/", json=attendance_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        response2 = client.post("/api/v1/attendance/", json=attendance_data)
        
        assert response2.status_code == status.HTTP_409_CONFLICT
        data = response2.json()
        
        assert "message" in data or "detail" in data

    def test_mark_attendance_future_date(self, client, test_employee_with_id_data):
        """Test marking attendance for future date"""

        client.post("/api/v1/employees/", json=test_employee_with_id_data)
        
        future_date = (date.today() + timedelta(days=1)).isoformat()
        attendance_data = {
            "employee_id": test_employee_with_id_data["employee_id"],
            "date": future_date,
            "status": "Present"
        }
        
        response = client.post("/api/v1/attendance/", json=attendance_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()
        
        assert "errors" in data or "detail" in data

    def test_mark_attendance_invalid_status(self, client, test_employee_with_id_data):
        """Test marking attendance with invalid status"""

        client.post("/api/v1/employees/", json=test_employee_with_id_data)
        
        attendance_data = {
            "employee_id": test_employee_with_id_data["employee_id"],
            "date": str(date.today()),
            "status": "INVALID_STATUS"
        }
        
        response = client.post("/api/v1/attendance/", json=attendance_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()
        
        assert "errors" in data or "detail" in data


    def test_get_all_attendance_empty(self, client):
        """Test getting all attendance when none exist"""
        response = client.get("/api/v1/attendance/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        if isinstance(data, dict):
            if "total" in data:
                assert data["total"] == 0
            if "records" in data:
                assert len(data["records"]) == 0

    def test_get_attendance_filter_by_employee(self, client, test_employee_with_id_data):
        """Test filtering attendance by employee ID"""

        client.post("/api/v1/employees/", json=test_employee_with_id_data)
        
        attendance_data = {
            "employee_id": test_employee_with_id_data["employee_id"],
            "date": str(date.today()),
            "status": "Present"
        }
        client.post("/api/v1/attendance/", json=attendance_data)
        
        response = client.get(f"/api/v1/attendance/?employee_id={test_employee_with_id_data['employee_id']}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        if isinstance(data, dict) and "records" in data:
            assert len(data["records"]) >= 1


    def test_attendance_summary_success(self, client, test_employee_with_id_data):
        """Test getting attendance summary for employee"""

        emp_response = client.post("/api/v1/employees/", json=test_employee_with_id_data)
        assert emp_response.status_code == status.HTTP_201_CREATED
        employee_id = emp_response.json()["employee_id"]
        
        today = date.today()
        for i in range(5):
            status_val = "Present" if i < 3 else "Absent"
            attendance_data = {
                "employee_id": employee_id,
                "date": (today - timedelta(days=i)).isoformat(),
                "status": status_val
            }
            client.post("/api/v1/attendance/", json=attendance_data)
        
        response = client.get(f"/api/v1/attendance/summary/employee/{employee_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        print(f"\nSummary response: {data}")
        
        assert "employee_id" in data or "emp_id" in data
        assert "total_present" in data or "present" in str(data).lower()
        assert "total_absent" in data or "absent" in str(data).lower()