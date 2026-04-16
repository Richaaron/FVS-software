"""
Student routes
"""
from flask import Blueprint, request, jsonify, current_app
from models import db, Student, StudentClass
from datetime import datetime
from .auth_utils import require_auth, require_role
from .id_generator import generate_admission_number, save_student_photo, delete_photo
from .validation_utils import validate_name

student_bp = Blueprint('student', __name__, url_prefix='/api/students')

@student_bp.route('', methods=['POST'])
@require_role('admin')
def create_student():
    """Create a new student with auto-generated admission number"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            photo_file = None
        else:
            data = request.form.to_dict()
            photo_file = request.files.get('photo')
        
        required = ['school_id', 'class_id', 'first_name', 'last_name']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields: school_id, class_id, first_name, last_name'}), 400
        
        # Validate names
        is_valid, error_msg = validate_name(data['first_name'], 'First name')
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        is_valid, error_msg = validate_name(data['last_name'], 'Last name')
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Auto-generate admission number
        school_id = int(data['school_id'])
        class_id = int(data['class_id'])
        admission_number = generate_admission_number(school_id, class_id)
        
        student = Student(
            school_id=school_id,
            class_id=class_id,
            admission_number=admission_number,
            first_name=data['first_name'],
            last_name=data['last_name'],
            middle_name=data.get('middle_name'),
            date_of_birth=datetime.fromisoformat(data['date_of_birth']) if data.get('date_of_birth') else None,
            gender=data.get('gender'),
            email=data.get('email'),
            phone=data.get('phone'),
            parent_name=data.get('parent_name'),
            parent_phone=data.get('parent_phone'),
            is_active=data.get('is_active', 'true').lower() == 'true'
        )
        
        db.session.add(student)
        db.session.flush()  # Get student ID before committing
        
        # Handle photo upload
        if photo_file:
            success, filename, error = save_student_photo(photo_file, student.id)
            if success:
                student.photo_filename = filename
            else:
                current_app.logger.warning(f"Failed to save student photo: {error}")
        
        db.session.commit()
        
        student_dict = student.to_dict()
        student_dict['auto_generated_credentials'] = {
            'admission_number': admission_number,
            'note': 'Admission number auto-generated'
        }
        
        return jsonify(student_dict), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Student creation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@student_bp.route('', methods=['GET'])
@require_auth
def get_students():
    """Get all students or filter by school/class"""
    try:
        school_id = request.args.get('school_id', type=int)
        class_id = request.args.get('class_id', type=int)
        
        query = Student.query
        
        if school_id:
            query = query.filter_by(school_id=school_id)
        if class_id:
            query = query.filter_by(class_id=class_id)
        
        students = query.all()
        return jsonify([student.to_dict() for student in students]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>', methods=['GET'])
@require_auth
def get_student(student_id):
    """Get student details"""
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        return jsonify(student.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>', methods=['PUT'])
@require_role('admin')
def update_student(student_id):
    """Update student information"""
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        data = request.get_json()
        
        if 'first_name' in data:
            student.first_name = data['first_name']
        if 'last_name' in data:
            student.last_name = data['last_name']
        if 'middle_name' in data:
            student.middle_name = data['middle_name']
        if 'email' in data:
            student.email = data['email']
        if 'parent_name' in data:
            student.parent_name = data['parent_name']
        if 'parent_phone' in data:
            student.parent_phone = data['parent_phone']
        if 'is_active' in data:
            student.is_active = data['is_active']
        
        db.session.commit()
        return jsonify(student.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/<int:student_id>', methods=['DELETE'])
@require_role('admin')
def delete_student(student_id):
    """Delete student"""
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        db.session.delete(student)
        db.session.commit()
        
        return jsonify({'message': 'Student deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
