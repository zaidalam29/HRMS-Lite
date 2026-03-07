# HRMS Lite Backend

A production-ready FastAPI backend for Human Resource Management System Lite with PostgreSQL database.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Step-by-Step Installation](#step-by-step-installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [API Usage Examples](#api-usage-examples)
- [Error Handling Examples](#error-handling-examples)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Deployment](#deployment)
- [Quick Start (5 Minutes)](#quick-start-5-minutes)

---

## Project Overview

HRMS Lite Backend is a RESTful API service that provides:

| Feature | Description |
|---------|-------------|
| **Employee Management** | Create, read, update, and delete employee records |
| **Attendance Tracking** | Mark and track daily attendance for employees |
| **Auto-generated Employee IDs** | Unique employee IDs generated automatically if not provided |
| **Production-grade Error Handling** | Comprehensive error management with proper HTTP status codes |
| **Comprehensive Testing** | 40+ test cases covering all scenarios |

---

## Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Framework** | FastAPI | 0.104.1 |
| **Database** | PostgreSQL | 14+ |
| **ORM** | SQLAlchemy | 2.0.23 |
| **Migrations** | Alembic | 1.12.1 |
| **Validation** | Pydantic | 2.5.0 |
| **Testing** | Pytest | 7.4.3 |
| **Server** | Uvicorn | 0.24.0 |

---

## Prerequisites

Before starting, ensure you have installed:

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.10+ | `python --version` |
| PostgreSQL | 14+ | `psql --version` |
| Git | Latest | `git --version` |
| pip | Latest | `pip --version` |

---

## Step-by-Step Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/zaidalam29/HRMS-Lite.git

# Navigate to backend directory
cd HRMS-Lite/backend
```

### Step 2: Create Virtual Environment

**Windows (Command Prompt):**

```bash
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
# Check installed packages
pip list
```

---

## Configuration

### Step 1: Create Environment File

```bash
# Copy example environment file
cp .env.example .env
```

### Step 2: Configure Environment Variables

Open `.env` file and update:

```env
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here-change-in-production

# Database - IMPORTANT: Password should NOT contain @ symbol
DATABASE_URL=postgresql://postgres:YourPassword123@localhost:5432/hrms_db

# CORS - Frontend URLs (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=INFO
```

> ⚠️ **IMPORTANT RULES:**
> - Password must **NOT** contain `@` symbol
> - Use only alphanumeric characters in password
> - ✅ Good password: `Postgres123`
> - ❌ Bad password: `Postgres@123`

---

## Database Setup

### Step 1: Start PostgreSQL

**Using Laragon:**
1. Open Laragon
2. Click "Start All"
3. Ensure PostgreSQL is running (green icon)

**Using Windows Services:**
```bash
net start postgresql-14
```

### Step 2: Create Database

```bash
# Connect to PostgreSQL
psql -U postgres -h localhost

# Create database (run in psql)
CREATE DATABASE hrms_db;

# Create test database (for running tests)
CREATE DATABASE hrms_test_db;

# Exit psql
\q
```

### Step 3: Verify Databases

```bash
# List all databases
psql -U postgres -l
```

### Step 4: Run Database Migrations

```bash
# Set database URL (PowerShell)
$env:DATABASE_URL = "postgresql://postgres:YourPassword123@localhost:5432/hrms_db"

# Create initial migration
alembic revision --autogenerate -m "Create employees and attendance tables"

# Apply migration
alembic upgrade head
```

### Step 5: Verify Tables Created

```bash
# Connect to database
psql -U postgres -d hrms_db

# List tables
\dt

# Expected output:
#          List of relations
# Schema |    Name     | Type  | Owner
#--------+-------------+-------+-------
# public | alembic_version | table | postgres
# public | employees   | table | postgres
# public | attendance  | table | postgres
```

---

## Running the Application

### Start Development Server

```bash
# With auto-reload (for development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Production Server

```bash
# Without auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access the Application

| Resource | URL |
|----------|-----|
| API Root | http://localhost:8000/ |
| Swagger Documentation | http://localhost:8000/api/docs |
| ReDoc Documentation | http://localhost:8000/api/redoc |
| Health Check | http://localhost:8000/health |

---

## API Endpoints

### Employee Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/api/v1/employees/` | Create employee | `{full_name, email, department, employee_id?}` |
| GET | `/api/v1/employees/` | List all employees | Query: `skip, limit, department` |
| GET | `/api/v1/employees/{employee_id}` | Get employee by ID | - |
| PUT | `/api/v1/employees/{employee_id}` | Update employee | `{full_name?, email?, department?}` |
| DELETE | `/api/v1/employees/{employee_id}` | Delete employee | - |

### Attendance Endpoints

| Method | Endpoint | Description | Request Body / Query |
|--------|----------|-------------|----------------------|
| POST | `/api/v1/attendance/` | Mark attendance | `{employee_id, date, status, notes?}` |
| GET | `/api/v1/attendance/` | List attendance | Query: `employee_id, start_date, end_date, status` |
| GET | `/api/v1/attendance/employee/{employee_id}` | Get employee attendance | Query: `start_date, end_date` |
| GET | `/api/v1/attendance/{attendance_id}` | Get attendance by ID | - |
| PUT | `/api/v1/attendance/{attendance_id}` | Update attendance | `{status?, notes?}` |
| DELETE | `/api/v1/attendance/{attendance_id}` | Delete attendance | - |
| GET | `/api/v1/attendance/summary/employee/{employee_id}` | Attendance summary | Query: `start_date, end_date` |

---

## API Usage Examples

### 1. Create Employee (Auto-generated ID)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/employees/" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "department": "Engineering"
  }'
```

**Response (201 Created):**
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "department": "Engineering",
  "id": 1,
  "employee_id": "EMP7F3D2A9B",
  "created_at": "2026-03-07T12:00:00",
  "updated_at": null
}
```

### 2. Create Employee (Custom ID)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/employees/" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "full_name": "Jane Smith",
    "email": "jane.smith@example.com",
    "department": "Marketing"
  }'
```

**Response (201 Created):**
```json
{
  "full_name": "Jane Smith",
  "email": "jane.smith@example.com",
  "department": "Marketing",
  "id": 2,
  "employee_id": "EMP001",
  "created_at": "2026-03-07T12:01:00",
  "updated_at": null
}
```

### 3. Get All Employees

**Request:**
```bash
curl "http://localhost:8000/api/v1/employees/?skip=0&limit=10"
```

**Response (200 OK):**
```json
{
  "total": 2,
  "employees": [
    {
      "id": 1,
      "employee_id": "EMP7F3D2A9B",
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "department": "Engineering",
      "created_at": "2026-03-07T12:00:00",
      "updated_at": null
    },
    {
      "id": 2,
      "employee_id": "EMP001",
      "full_name": "Jane Smith",
      "email": "jane.smith@example.com",
      "department": "Marketing",
      "created_at": "2026-03-07T12:01:00",
      "updated_at": null
    }
  ]
}
```

### 4. Get Employee by ID

**Request:**
```bash
curl "http://localhost:8000/api/v1/employees/EMP001"
```

**Response (200 OK):**
```json
{
  "id": 2,
  "employee_id": "EMP001",
  "full_name": "Jane Smith",
  "email": "jane.smith@example.com",
  "department": "Marketing",
  "created_at": "2026-03-07T12:01:00",
  "updated_at": null
}
```

### 5. Update Employee

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/v1/employees/EMP001" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Updated",
    "department": "Sales"
  }'
```

**Response (200 OK):**
```json
{
  "id": 2,
  "employee_id": "EMP001",
  "full_name": "Jane Updated",
  "email": "jane.smith@example.com",
  "department": "Sales",
  "created_at": "2026-03-07T12:01:00",
  "updated_at": "2026-03-07T12:05:00"
}
```

### 6. Delete Employee

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/employees/EMP001"
```

**Response:** `204 No Content`

### 7. Mark Attendance

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/attendance/" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP7F3D2A9B",
    "date": "2026-03-07",
    "status": "Present",
    "notes": "On time"
  }'
```

**Response (201 Created):**
```json
{
  "employee_id": "EMP7F3D2A9B",
  "date": "2026-03-07",
  "status": "Present",
  "notes": "On time",
  "id": 1,
  "employee_name": "John Doe"
}
```

### 8. Get Attendance Records

**Request:**
```bash
curl "http://localhost:8000/api/v1/attendance/?employee_id=EMP7F3D2A9B&start_date=2026-03-01&end_date=2026-03-07"
```

**Response (200 OK):**
```json
{
  "total": 5,
  "records": [
    {
      "id": 1,
      "employee_id": "EMP7F3D2A9B",
      "date": "2026-03-07",
      "status": "Present",
      "notes": "On time",
      "employee_name": "John Doe"
    },
    {
      "id": 2,
      "employee_id": "EMP7F3D2A9B",
      "date": "2026-03-06",
      "status": "Present",
      "notes": null,
      "employee_name": "John Doe"
    }
  ]
}
```

### 9. Get Attendance Summary

**Request:**
```bash
curl "http://localhost:8000/api/v1/attendance/summary/employee/EMP7F3D2A9B?start_date=2026-03-01&end_date=2026-03-07"
```

**Response (200 OK):**
```json
{
  "employee_id": "EMP7F3D2A9B",
  "employee_name": "John Doe",
  "total_present": 5,
  "total_absent": 2,
  "total_records": 7
}
```

---

## Error Handling Examples

### 1. Validation Error (422)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/employees/" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "invalid-email",
    "department": "Engineering"
  }'
```

**Response (422 Unprocessable Entity):**
```json
{
  "message": "Validation failed",
  "errors": {
    "email": "value is not a valid email address"
  },
  "error_code": "VALIDATION_ERROR"
}
```

### 2. Employee Not Found (404)

**Request:**
```bash
curl "http://localhost:8000/api/v1/employees/EMP999999"
```

**Response (404 Not Found):**
```json
{
  "detail": {
    "message": "Employee with ID 'EMP999999' not found",
    "error_code": "EMPLOYEE_NOT_FOUND"
  }
}
```

### 3. Duplicate Email (409)

**Response (409 Conflict):**
```json
{
  "detail": {
    "message": "Employee with email 'john@example.com' already exists",
    "error_code": "DUPLICATE_EMPLOYEE"
  }
}
```

### 4. Duplicate Attendance (409)

**Response (409 Conflict):**
```json
{
  "detail": {
    "message": "Attendance already marked for employee 'EMP7F3D2A9B' on 2026-03-07",
    "error_code": "DUPLICATE_ATTENDANCE"
  }
}
```

---

## Testing

### Test Database Setup

```bash
# Create test database
psql -U postgres -c "CREATE DATABASE hrms_test_db;"

# Verify test database created
psql -U postgres -l | findstr hrms_test_db
```

### Run All Tests

```bash
# Activate virtual environment
venv\Scripts\activate

# Run all tests
pytest
```

### Run Tests with Coverage

```bash
# Run tests with coverage report
pytest --cov=app tests/ --cov-report=html

# Open coverage report (Windows)
start htmlcov/index.html
```

### Run Specific Test Files

```bash
# Run only employee tests
pytest tests/test_employees.py -v

# Run only attendance tests
pytest tests/test_attendance.py -v
```

### Run Specific Test Cases

```bash
# Run a single test
pytest tests/test_employees.py::TestEmployeeAPI::test_create_employee_without_id_success -v

# Run with print statements
pytest tests/test_attendance.py::TestAttendanceAPI::test_attendance_summary_success -v -s
```

### Test Categories

| Test File | Number of Tests | Description |
|-----------|-----------------|-------------|
| `test_employees.py` | 15+ | Employee CRUD operations, validation, error handling |
| `test_attendance.py` | 25+ | Attendance marking, filtering, summaries, error handling |

### Expected Test Output

```text
================================= test session starts =================================
collected 41 items

tests/test_employees.py ......................                                  [ 50%]
tests/test_attendance.py ....................                                   [100%]

================================= 41 passed in 3.45s =================================
```

---

## Project Structure

```text
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   │
│   ├── core/                   # Core configurations
│   │   ├── __init__.py
│   │   ├── config.py           # Environment configuration
│   │   ├── database.py         # Database connection
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── logging_config.py   # Logging setup
│   │
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── employee.py         # Employee model
│   │   └── attendance.py       # Attendance model
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── employee.py         # Employee schemas
│   │   └── attendance.py       # Attendance schemas
│   │
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependencies
│   │   └── v1/                 # API version 1
│   │       ├── __init__.py
│   │       ├── employees.py    # Employee endpoints
│   │       └── attendance.py   # Attendance endpoints
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── employee_service.py # Employee service
│   │   └── attendance_service.py # Attendance service
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       └── validators.py       # Validators
│
├── tests/                      # Tests
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_employees.py       # Employee tests
│   └── test_attendance.py      # Attendance tests
│
├── alembic/                    # Migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── .env.example
├── .gitignore
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Troubleshooting

### 1. Database Connection Error

**Error:**
```text
connection to server at "localhost" (::1), port 5432 failed
```

**Solution:**
```bash
# Check if PostgreSQL is running
net start postgresql-14

# Test connection
psql -U postgres -d hrms_db -c "SELECT 1"
```

### 2. Alembic Migration Fails

**Error:**
```text
FileNotFoundError: [Errno 2] No such file or directory: 'alembic\script.py.mako'
```

**Solution:**
```bash
# Reinitialize alembic
alembic init alembic
```

### 3. Tables Not Created

**Error:**
```text
relation "employees" does not exist
```

**Solution:**
```bash
# Run migrations
alembic upgrade head

# Check tables
psql -U postgres -d hrms_db -c "\dt"
```

### 4. Port Already in Use

**Error:**
```text
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Solution:**
```bash
# Find process using port
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### 5. Password with @ Symbol

**Error:** URL parsing errors

**Solution:**
```sql
-- Change PostgreSQL password
psql -U postgres
ALTER USER postgres WITH PASSWORD 'YourNewPassword123';
\q
```
Then update `.env` file:
```env
DATABASE_URL=postgresql://postgres:YourNewPassword123@localhost:5432/hrms_db
```

### 6. Tests Failing with 500 Error

**Error:**
```text
assert 500 == 409
```

**Solution:** Check exception handling in endpoint:
```python
# In app/api/v1/employees.py
except DuplicateEmployeeError as e:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "message": str(e),
            "error_code": "DUPLICATE_EMPLOYEE"
        }
    )
```

---

## Deployment

### Deploy to Render

1. Push code to GitHub
2. Create account on [render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:

| Configuration | Value |
|---------------|-------|
| Name | `hrms-lite-api` |
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

6. Add environment variables:
   - `DATABASE_URL`: Your production PostgreSQL URL
   - `ENVIRONMENT`: `production`
   - `SECRET_KEY`: Your secret key
   - `CORS_ORIGINS`: Your frontend URL
7. Click "Create Web Service"

### Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

### Production Environment Variables

```env
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-strong-secret-key-here
DATABASE_URL=postgresql://user:password@host:5432/database
CORS_ORIGINS=https://your-frontend-domain.com
LOG_LEVEL=WARNING
```

---

## Quick Start (5 Minutes)

```bash
# 1. Clone and enter
git clone https://github.com/zaidalam29/HRMS-Lite.git
cd HRMS-Lite/backend

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your database credentials

# 5. Create database
psql -U postgres -c "CREATE DATABASE hrms_db;"
psql -U postgres -c "CREATE DATABASE hrms_test_db;"

# 6. Run migrations
alembic upgrade head

# 7. Start server
uvicorn app.main:app --reload

# 8. Open API docs
# http://localhost:8000/api/docs
```

---

## Support

For issues and questions:
- Check [Troubleshooting](#troubleshooting) section
- Review error logs
- Create a GitHub issue

---

## License

This project is created for assignment purposes only.

---

## Author

**Zaid Alam**

- GitHub: [@zaidalam29](https://github.com/zaidalam29)
- Email: zaidalam29@gmail.com

---

