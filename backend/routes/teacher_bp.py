"""
Teacher routes
"""
from flask import Blueprint, request, jsonify
from models import db, Teacher, User
from datetime import datetime
from .auth_utils import require_auth, require_role
from .teacher_utils import generate_username, generate_password

teacher_bp = Blueprint('teacher', __name__, url_prefix='/api/teachers')

@teacher_bp.route('', methods=['POST'])
@require_role('admin')
def create_teacher():
    """Create a new teacher with auto-generated credentials"""
    try:
        data = request.get_json()
        
        required = ['school_id', 'staff_id', 'first_name', 'last_name', 'email']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields: school_id, staff_id, first_name, last_name, email'}), 400
        
        # Check if teacher with same staff_id exists
        existing_staff = Teacher.query.filter_by(staff_id=data['staff_id']).first()
        if existing_staff:
            return jsonify({'error': 'Staff ID already exists'}), 400
        
        # Check if email already has a user account
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already in use'}), 400
        
        # Generate unique username and password
        username = generate_username(data['first_name'], data['last_name'], data['staff_id'])
        password = generate_password(12)
        
        # Create User account for teacher
        user = User(
            username=username,
            email=data['email'],
            role='teacher',
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Flush to get the user.id before committing
        
        # Create Teacher record
        teacher = Teacher(
            user_id=user.id,
            school_id=data['school_id'],
            staff_id=data['staff_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            qualification=data.get('qualification'),
            specialization=data.get('specialization'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(teacher)
        db.session.commit()
        
        # Return teacher info WITH auto-generated credentials
        response = teacher.to_dict()
        response['user_id'] = user.id
        response['auto_generated_credentials'] = {
            'username': username,
            'password': password,
            'email': data['email'],
            'note': 'These credentials are auto-generated. Teacher should change password on first login.'
        }
        
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('', methods=['GET'])
@require_auth
def get_teachers():
    """Get all teachers"""
    try:
        school_id = request.args.get('school_id', type=int)
        
        query = Teacher.query
        if school_id:
            query = query.filter_by(school_id=school_id)
        
        teachers = query.all()
        return jsonify([teacher.to_dict() for teacher in teachers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/<int:teacher_id>', methods=['GET'])
@require_auth
def get_teacher(teacher_id):
    """Get teacher details"""
    try:
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        return jsonify(teacher.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/<int:teacher_id>', methods=['PUT'])
@require_role('admin')
def update_teacher(teacher_id):
    """Update teacher information"""
    try:
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        data = request.get_json()
        
        if 'first_name' in data:
            teacher.first_name = data['first_name']
        if 'last_name' in data:
            teacher.last_name = data['last_name']
        if 'email' in data:
            teacher.email = data['email']
        if 'phone' in data:
            teacher.phone = data['phone']
        if 'qualification' in data:
            teacher.qualification = data['qualification']
        if 'specialization' in data:
            teacher.specialization = data['specialization']
        if 'is_active' in data:
            teacher.is_active = data['is_active']
        
        db.session.commit()
        return jsonify(teacher.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
