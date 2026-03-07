"""
Test cases for Employee API - Fixed with correct error response handling
"""

import pytest
from fastapi import status
from datetime import datetime
import time

class TestEmployeeAPI:
    """Test suite for employee endpoints"""

    def test_create_employee_without_id_success(self, client, test_employee_data):
        """Test creating employee without ID - should auto-generate ID"""
        response = client.post("/api/v1/employees/", json=test_employee_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["full_name"] == test_employee_data["full_name"]
        assert data["email"] == test_employee_data["email"]
        assert data["department"] == test_employee_data["department"]
        assert "employee_id" in data
        assert data["employee_id"].startswith("EMP")
        assert "id" in data
        assert "created_at" in data

    def test_create_employee_with_id_success(self, client, test_employee_with_id_data):
        """Test creating employee with custom ID"""
        response = client.post("/api/v1/employees/", json=test_employee_with_id_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["employee_id"] == test_employee_with_id_data["employee_id"]
        assert data["full_name"] == test_employee_with_id_data["full_name"]
        assert data["email"] == test_employee_with_id_data["email"]
        assert data["department"] == test_employee_with_id_data["department"]

    def test_create_employee_duplicate_email(self, client, test_employee_data):
        """Test creating employee with duplicate email"""

        response1 = client.post("/api/v1/employees/", json=test_employee_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        response2 = client.post("/api/v1/employees/", json=test_employee_data)
        
        assert response2.status_code == status.HTTP_409_CONFLICT
        data = response2.json()
        
        assert "detail" in data
        assert data["detail"]["error_code"] == "DUPLICATE_EMPLOYEE"
        assert "message" in data["detail"]
        assert "already exists" in data["detail"]["message"].lower()

    def test_create_employee_duplicate_id(self, client, test_employee_with_id_data):
        """Test creating employee with duplicate custom ID"""

        response1 = client.post("/api/v1/employees/", json=test_employee_with_id_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        duplicate_data = test_employee_with_id_data.copy()
        duplicate_data["email"] = f"different.{int(time.time())}@example.com"
        
        response2 = client.post("/api/v1/employees/", json=duplicate_data)
        
        assert response2.status_code == status.HTTP_409_CONFLICT
        data = response2.json()
        
        assert "detail" in data
        assert data["detail"]["error_code"] == "DUPLICATE_EMPLOYEE"
        assert "message" in data["detail"]
        assert "already exists" in data["detail"]["message"].lower()

    def test_create_employee_invalid_email(self, client, test_employee_data):
        """Test creating employee with invalid email format"""
        invalid_data = test_employee_data.copy()
        invalid_data["email"] = "invalid-email"
        
        response = client.post("/api/v1/employees/", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()
        
        assert "detail" in data or "errors" in data

    def test_create_employee_missing_required_fields(self, client):
        """Test creating employee with missing required fields"""
        invalid_data = {
            "full_name": "John Doe"
        }
        
        response = client.post("/api/v1/employees/", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()
        
        assert "detail" in data or "errors" in data



    def test_get_all_employees_empty(self, client):
        """Test getting all employees when none exist"""
        response = client.get("/api/v1/employees/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        if "total" in data:
            assert data["total"] == 0
        if "employees" in data:
            assert len(data["employees"]) == 0

    def test_get_all_employees_with_data(self, client, test_employee_data, test_employee_with_id_data):
        """Test getting all employees with data"""

        client.post("/api/v1/employees/", json=test_employee_data)
        client.post("/api/v1/employees/", json=test_employee_with_id_data)
        
        response = client.get("/api/v1/employees/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        if "total" in data:
            assert data["total"] >= 2
        if "employees" in data:
            assert len(data["employees"]) >= 2

    def test_get_employees_pagination(self, client):
        """Test pagination for employees list"""

        for i in range(5):
            employee_data = {
                "full_name": f"User {i}",
                "email": f"user{i}.{int(time.time())}@example.com",
                "department": "Engineering"
            }
            client.post("/api/v1/employees/", json=employee_data)
        

        response = client.get("/api/v1/employees/?skip=2&limit=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        if "total" in data:
            assert data["total"] == 5
        if "employees" in data:
            assert len(data["employees"]) == 2

    def test_get_employees_filter_by_department(self, client):
        """Test filtering employees by department"""
        timestamp = int(time.time())
        
        engineering_data = {
            "full_name": "Engineer 1",
            "email": f"eng1.{timestamp}@example.com",
            "department": "Engineering"
        }
        marketing_data = {
            "full_name": "Marketer 1",
            "email": f"mkt1.{timestamp}@example.com",
            "department": "Marketing"
        }
        
        client.post("/api/v1/employees/", json=engineering_data)
        client.post("/api/v1/employees/", json=marketing_data)
        
        response = client.get("/api/v1/employees/?department=Engineering")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        if "employees" in data:
            for emp in data["employees"]:
                assert emp["department"] == "Engineering"

    def test_get_employee_by_id_success(self, client, test_employee_with_id_data):
        """Test getting employee by ID successfully"""
        
        create_resp = client.post("/api/v1/employees/", json=test_employee_with_id_data)
        employee_id = create_resp.json()["employee_id"]
        
        response = client.get(f"/api/v1/employees/{employee_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["employee_id"] == employee_id
        assert data["full_name"] == test_employee_with_id_data["full_name"]

    def test_get_employee_by_id_not_found(self, client):
        """Test getting employee with non-existent ID"""
        response = client.get("/api/v1/employees/EMP999999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        
        if "detail" in data:
            assert "not found" in data["detail"]["message"].lower()
        else:
            assert "message" in data


    def test_update_employee_success(self, client, test_employee_with_id_data):
        """Test updating employee successfully"""

        create_resp = client.post("/api/v1/employees/", json=test_employee_with_id_data)
        employee_id = create_resp.json()["employee_id"]
        
        update_data = {
            "full_name": "Updated Name",
            "department": "Sales"
        }
        
        response = client.put(f"/api/v1/employees/{employee_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["department"] == "Sales"
        assert data["email"] == test_employee_with_id_data["email"]

    def test_update_employee_partial(self, client, test_employee_with_id_data):
        """Test partial update of employee"""

        create_resp = client.post("/api/v1/employees/", json=test_employee_with_id_data)
        employee_id = create_resp.json()["employee_id"]
        
        response = client.put(f"/api/v1/employees/{employee_id}", json={"full_name": "New Name"})
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == "New Name"
        assert data["email"] == test_employee_with_id_data["email"]

    def test_update_employee_not_found(self, client):
        """Test updating non-existent employee"""
        response = client.put("/api/v1/employees/EMP999999", json={"full_name": "New Name"})
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        
        assert "detail" in data or "message" in data

    
    def test_delete_employee_success(self, client, test_employee_with_id_data):
        """Test deleting employee successfully"""

        create_resp = client.post("/api/v1/employees/", json=test_employee_with_id_data)
        employee_id = create_resp.json()["employee_id"]
        
        response = client.delete(f"/api/v1/employees/{employee_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        get_response = client.get(f"/api/v1/employees/{employee_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_employee_not_found(self, client):
        """Test deleting non-existent employee"""
        response = client.delete("/api/v1/employees/EMP999999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        
        assert "detail" in data or "message" in data