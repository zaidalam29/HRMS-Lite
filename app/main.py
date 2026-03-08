"""
Main application entry point with error handlers and middleware
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
import time
from typing import Union
import traceback
import os
import uvicorn

from app.core.config import settings
from app.core.exceptions import (
    HRMSException,
    EmployeeNotFoundError,
    DuplicateEmployeeError,
    AttendanceNotFoundError,
    DuplicateAttendanceError
)
from app.api.v1 import employees, attendance
from app.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HRMS Lite API",
    description="Human Resource Management System Lite",
    version="1.0.0",
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    request_id = request.headers.get("X-Request-ID", str(time.time()))
    
    logger.info(f"Request started: {request.method} {request.url.path} [ID: {request_id}]")
    
    try:
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"Status: {response.status_code} Time: {process_time:.3f}s [ID: {request_id}]"
        )
        
        return response
    except Exception as e:
        logger.error(
            f"Request failed: {request.method} {request.url.path} "
            f"Error: {str(e)} [ID: {request_id}]",
            exc_info=True
        )
        raise

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors with detailed field errors"""
    errors = {}
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:]) 
        errors[field] = error["msg"]
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation failed",
            "errors": errors,
            "error_code": "VALIDATION_ERROR"
        }
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors"""
    error_msg = str(exc.orig)
    
    if "duplicate key" in error_msg.lower():
        if "employees_employee_id_key" in error_msg:
            return JSONResponse(
                status_code=409,
                content={
                    "success": False,
                    "message": "Employee ID already exists",
                    "error_code": "DUPLICATE_EMPLOYEE_ID"
                }
            )
        elif "employees_email_key" in error_msg:
            return JSONResponse(
                status_code=409,
                content={
                    "success": False,
                    "message": "Email already registered",
                    "error_code": "DUPLICATE_EMAIL"
                }
            )
        elif "unique_attendance_per_day" in error_msg:
            return JSONResponse(
                status_code=409,
                content={
                    "success": False,
                    "message": "Attendance already marked for this employee on this date",
                    "error_code": "DUPLICATE_ATTENDANCE"
                }
            )
    
    logger.error(f"Database integrity error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Database error occurred",
            "error_code": "DATABASE_ERROR"
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy errors"""
    logger.error(f"Database error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Database operation failed",
            "error_code": "DATABASE_ERROR"
        }
    )

@app.exception_handler(EmployeeNotFoundError)
async def employee_not_found_handler(request: Request, exc: EmployeeNotFoundError):
    """Handle employee not found errors"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": str(exc),
            "error_code": "EMPLOYEE_NOT_FOUND"
        }
    )

@app.exception_handler(DuplicateEmployeeError)
async def duplicate_employee_handler(request: Request, exc: DuplicateEmployeeError):
    """Handle duplicate employee errors"""
    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "message": str(exc),
            "error_code": "DUPLICATE_EMPLOYEE"
        }
    )

@app.exception_handler(AttendanceNotFoundError)
async def attendance_not_found_handler(request: Request, exc: AttendanceNotFoundError):
    """Handle attendance not found errors"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": str(exc),
            "error_code": "ATTENDANCE_NOT_FOUND"
        }
    )

@app.exception_handler(HRMSException)
async def hrms_exception_handler(request: Request, exc: HRMSException):
    """Handle custom HRMS exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.error_code,
            **exc.details
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )

app.include_router(employees.router, prefix="/api/v1/employees", tags=["Employees"])
app.include_router(attendance.router, prefix="/api/v1/attendance", tags=["Attendance"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to HRMS Lite API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT
    }
    

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)   
    