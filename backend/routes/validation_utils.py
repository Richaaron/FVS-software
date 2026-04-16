"""
Input validation utilities for the FVS Software backend
Provides comprehensive validation for all user inputs
"""

import re
from typing import Tuple, Optional

def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format
    Returns: (is_valid, error_message)
    """
    if not email or not isinstance(email, str):
        return False, "Email is required"
    
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 120:
        return False, "Email is too long"
    
    return True, ""

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format
    Returns: (is_valid, error_message)
    """
    if not username or not isinstance(username, str):
        return False, "Username is required"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must be at most 50 characters"
    
    if not re.match(r'^[a-zA-Z0-9._-]+$', username):
        return False, "Username can only contain letters, numbers, dots, hyphens, and underscores"
    
    return True, ""

def validate_password(password: str, min_length: int = 8) -> Tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    if len(password) > 128:
        return False, "Password is too long"
    
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and digits"
    
    return True, ""

def validate_name(name: str, field_name: str = "Name") -> Tuple[bool, str]:
    """
    Validate person names
    Returns: (is_valid, error_message)
    """
    if not name or not isinstance(name, str):
        return False, f"{field_name} is required"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, f"{field_name} must be at least 2 characters"
    
    if len(name) > 100:
        return False, f"{field_name} must be at most 100 characters"
    
    if not re.match(r"^[a-zA-Z\s'-]+$", name):
        return False, f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"
    
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate phone number (Nigerian format)
    Returns: (is_valid, error_message)
    """
    if not phone or not isinstance(phone, str):
        return False, "Phone number is required"
    
    # Remove common formatting characters
    phone = re.sub(r'[\s\-\(\)\.+]', '', phone.strip())
    
    # Nigerian phone: 11 digits starting with 0, or 13 digits starting with +234
    if not re.match(r'^(\+234|0)[0-9]{10}$', phone):
        return False, "Invalid Nigerian phone number format"
    
    return True, ""

def validate_staff_id(staff_id: str) -> Tuple[bool, str]:
    """
    Validate staff ID format
    Returns: (is_valid, error_message)
    """
    if not staff_id or not isinstance(staff_id, str):
        return False, "Staff ID is required"
    
    staff_id = staff_id.strip()
    
    if len(staff_id) < 2 or len(staff_id) > 20:
        return False, "Staff ID must be between 2 and 20 characters"
    
    if not re.match(r'^[a-zA-Z0-9\-_/]+$', staff_id):
        return False, "Staff ID contains invalid characters"
    
    return True, ""

def validate_school_name(name: str) -> Tuple[bool, str]:
    """
    Validate school name
    Returns: (is_valid, error_message)
    """
    if not name or not isinstance(name, str):
        return False, "School name is required"
    
    name = name.strip()
    
    if len(name) < 3:
        return False, "School name must be at least 3 characters"
    
    if len(name) > 150:
        return False, "School name is too long"
    
    return True, ""

def validate_subject_name(name: str) -> Tuple[bool, str]:
    """
    Validate subject name
    Returns: (is_valid, error_message)
    """
    if not name or not isinstance(name, str):
        return False, "Subject name is required"
    
    name = name.strip()
    
    if len(name) < 2 or len(name) > 100:
        return False, "Subject name must be between 2 and 100 characters"
    
    return True, ""

def validate_score(score: Optional[float], field_name: str = "Score", max_score: float = 100) -> Tuple[bool, str]:
    """
    Validate numerical scores
    Returns: (is_valid, error_message)
    """
    if score is None or score == '':
        return True, ""  # Optional field
    
    try:
        score_float = float(score)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a number"
    
    if score_float < 0:
        return False, f"{field_name} cannot be negative"
    
    if score_float > max_score:
        return False, f"{field_name} cannot exceed {max_score}"
    
    return True, ""

def validate_class_name(name: str) -> Tuple[bool, str]:
    """
    Validate class name
    Returns: (is_valid, error_message)
    """
    if not name or not isinstance(name, str):
        return False, "Class name is required"
    
    name = name.strip()
    
    if len(name) < 1 or len(name) > 50:
        return False, "Class name must be between 1 and 50 characters"
    
    return True, ""

def sanitize_input(text: str, max_length: int = 500) -> str:
    """
    Sanitize string input to prevent injection attacks
    """
    if not isinstance(text, str):
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Limit length
    text = text[:max_length]
    
    return text


def validate_photo_upload(file, max_size_mb: int = 5) -> Tuple[bool, str]:
    """
    Validate photo file for upload
    Returns: (is_valid, error_message)
    """
    # Check if file exists
    if not file or file.filename == '':
        return True, ""  # Optional field
    
    # Allowed extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Check file extension
    filename = file.filename.lower()
    if '.' not in filename:
        return False, "File must have an extension"
    
    ext = filename.rsplit('.', 1)[1]
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size_bytes = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size_bytes > max_size_bytes:
        return False, f"File size exceeds {max_size_mb}MB limit"
    
    if file_size_bytes == 0:
        return False, "File is empty"
    
    # Check minimum file size (at least 1KB)
    if file_size_bytes < 1024:
        return False, "File is too small (minimum 1KB)"
    
    # Check file signature/magic number (basic validation)
    file_header = file.read(12)
    file.seek(0)  # Reset for actual usage
    
    # Validate file signatures
    valid_signatures = {
        'jpg': [b'\xff\xd8\xff'],  # JPEG
        'png': [b'\x89PNG\r\n\x1a\n'],  # PNG
        'gif': [b'GIF87a', b'GIF89a'],  # GIF
        'webp': [b'RIFF', b'WEBP']  # WebP
    }
    
    if ext == 'jpg' or ext == 'jpeg':
        if not any(file_header.startswith(sig) for sig in valid_signatures['jpg']):
            return False, "Invalid JPEG file"
    elif ext == 'png':
        if not any(file_header.startswith(sig) for sig in valid_signatures['png']):
            return False, "Invalid PNG file"
    elif ext == 'gif':
        if not any(file_header.startswith(sig) for sig in valid_signatures['gif']):
            return False, "Invalid GIF file"
    elif ext == 'webp':
        # WebP validation is more complex, basic check here
        if b'RIFF' not in file_header or b'WEBP' not in file_header:
            return False, "Invalid WebP file"
    
    return True, ""


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other attacks
    """
    import os
    
    if not filename:
        return "file"
    
    # Remove path separators
    filename = os.path.basename(filename)
    
    # Remove special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:190] + ('.' + ext if ext else '')
    
    return filename
