"""
ID generation and image handling utilities
"""

import os
import uuid
import string
import random
from datetime import datetime
from models import db, Student, Teacher
from .validation_utils import validate_photo_upload, sanitize_filename

# Configure upload folders
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Create upload directories if they don't exist
os.makedirs(os.path.join(UPLOAD_FOLDER, 'students'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'teachers'), exist_ok=True)

def generate_admission_number(school_id: int, class_id: int = None) -> str:
    """
    Generate unique admission number
    Format: ADM-YYYY-SCHOOL-CLASS-SEQUENCE
    Example: ADM-2026-001-P3A-001
    
    Args:
        school_id: School ID
        class_id: Optional class ID
    
    Returns:
        Unique admission number
    """
    try:
        year = datetime.now().year
        
        # Get next sequence number for school/year
        last_student = Student.query.filter_by(school_id=school_id).order_by(Student.id.desc()).first()
        
        sequence = 1
        if last_student:
            # Extract sequence from last admission number
            parts = last_student.admission_number.split('-')
            if len(parts) > 1 and parts[-1].isdigit():
                sequence = int(parts[-1]) + 1
        
        # Format: ADM-2026-SCHOOLID-SEQUENCE
        admission_number = f"ADM-{year}-{school_id:03d}-{sequence:04d}"
        
        # Ensure uniqueness
        while Student.query.filter_by(admission_number=admission_number).first():
            sequence += 1
            admission_number = f"ADM-{year}-{school_id:03d}-{sequence:04d}"
        
        return admission_number
    except Exception as e:
        # Fallback: use UUID for safety
        return f"ADM-{uuid.uuid4().hex[:12].upper()}"

def generate_staff_id(school_id: int, teacher_id: int = None) -> str:
    """
    Generate unique staff ID
    Format: STAFF-SCHOOL-YEAR-SEQUENCE
    Example: STAFF-001-2026-001
    
    Args:
        school_id: School ID
        teacher_id: Optional teacher ID
    
    Returns:
        Unique staff ID
    """
    try:
        year = datetime.now().year
        
        # Get next sequence number for school/year
        last_teacher = Teacher.query.filter_by(school_id=school_id).order_by(Teacher.id.desc()).first()
        
        sequence = 1
        if last_teacher:
            # Extract sequence from last staff id
            parts = last_teacher.staff_id.split('-')
            if len(parts) > 1 and parts[-1].isdigit():
                sequence = int(parts[-1]) + 1
        
        # Format: STAFF-SCHOOLID-YEAR-SEQUENCE
        staff_id = f"STAFF-{school_id:03d}-{year}-{sequence:03d}"
        
        # Ensure uniqueness
        while Teacher.query.filter_by(staff_id=staff_id).first():
            sequence += 1
            staff_id = f"STAFF-{school_id:03d}-{year}-{sequence:03d}"
        
        return staff_id
    except Exception as e:
        # Fallback: use UUID for safety
        return f"STAFF-{uuid.uuid4().hex[:12].upper()}"

def allowed_file(filename: str) -> bool:
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_student_photo(file, student_id: int) -> tuple:
    """
    Save student photo with validation
    
    Args:
        file: FileStorage object from request
        student_id: Student ID
    
    Returns:
        (success: bool, filename: str, error: str)
    """
    try:
        # Validate file
        is_valid, error_msg = validate_photo_upload(file, max_size_mb=5)
        if not is_valid:
            return False, None, error_msg
        
        if not file or file.filename == '':
            return True, None, None  # Optional field
        
        # Generate unique filename with sanitization
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
        safe_name = sanitize_filename(f"student_{student_id}_{uuid.uuid4().hex[:8]}.{ext}")
        filename = safe_name
        
        # Save file
        filepath = os.path.join(UPLOAD_FOLDER, 'students', filename)
        file.save(filepath)
        
        return True, filename, None
    
    except Exception as e:
        return False, None, f"Photo upload error: {str(e)}"

def save_teacher_photo(file, teacher_id: int) -> tuple:
    """
    Save teacher photo with validation
    
    Args:
        file: FileStorage object from request
        teacher_id: Teacher ID
    
    Returns:
        (success: bool, filename: str, error: str)
    """
    try:
        # Validate file
        is_valid, error_msg = validate_photo_upload(file, max_size_mb=5)
        if not is_valid:
            return False, None, error_msg
        
        if not file or file.filename == '':
            return True, None, None  # Optional field
        
        # Generate unique filename with sanitization
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
        safe_name = sanitize_filename(f"teacher_{teacher_id}_{uuid.uuid4().hex[:8]}.{ext}")
        filename = safe_name
        
        # Save file
        filepath = os.path.join(UPLOAD_FOLDER, 'teachers', filename)
        file.save(filepath)
        
        return True, filename, None
    
    except Exception as e:
        return False, None, f"Photo upload error: {str(e)}"

def delete_photo(filename: str, photo_type: str = 'student') -> bool:
    """
    Delete a saved photo
    
    Args:
        filename: Filename to delete
        photo_type: 'student' or 'teacher'
    
    Returns:
        True if deleted, False otherwise
    """
    try:
        if not filename:
            return True
        
        filepath = os.path.join(UPLOAD_FOLDER, photo_type + 's', filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception as e:
        return False

def get_photo_url(filename: str, photo_type: str = 'student') -> str:
    """
    Get URL for accessing photo
    
    Args:
        filename: Filename
        photo_type: 'student' or 'teacher'
    
    Returns:
        URL path to photo
    """
    if not filename:
        return None
    return f"/api/photos/{photo_type}/{filename}"
