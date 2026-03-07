"""
Custom validation functions
"""

import re
from datetime import datetime, date
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)

def validate_email_format(email: str) -> bool:
    """
    Validate email format using regex
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_date_format(date_str: str) -> bool:
    """
    Validate date format (YYYY-MM-DD)
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def parse_date(date_input: Union[str, date, None]) -> Optional[date]:
    """
    Parse date from string or return date object
    """
    if date_input is None:
        return None
    
    if isinstance(date_input, date):
        return date_input
    
    if isinstance(date_input, str):
        try:
            return datetime.strptime(date_input, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid date format: {date_input}")
            raise ValueError(f"Invalid date format: {date_input}. Use YYYY-MM-DD")
    
    raise ValueError(f"Invalid date type: {type(date_input)}")

def validate_future_date(check_date: date) -> bool:
    """
    Check if date is not in future
    """
    return check_date <= date.today()

def sanitize_string(input_str: Optional[str]) -> Optional[str]:
    """
    Sanitize string input (remove extra spaces, etc.)
    """
    if input_str is None:
        return None
    
    cleaned = ' '.join(input_str.split())
    
    cleaned = re.sub(r'[<>"\'%;()&+]', '', cleaned)
    
    return cleaned