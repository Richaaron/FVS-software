"""
Teacher routes
"""
from flask import Blueprint, request, jsonify, current_app
from models import db, Teacher, User
from datetime import datetime
from .auth_utils import require_auth, require_role
from .teacher_utils import generate_username, generate_password
from .id_generator import generate_staff_id, save_teacher_photo
from .validation_utils import validate_name, validate_email
from .email_utils import send_credentials_email

teacher_bp = Blueprint('teacher', __name__, url_prefix='/api/teachers')

@teacher_bp.route('', methods=['POST'])
@require_role('admin')
def create_teacher():
    """Create a new teacher with auto-generated credentials and staff ID"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            photo_file = None
        else:
            data = request.form.to_dict()
            photo_file = request.files.get('photo')
        
        required = ['school_id', 'first_name', 'last_name', 'email']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields: school_id, first_name, last_name, email'}), 400
        
        # Validate inputs
        is_valid, error_msg = validate_name(data['first_name'], 'First name')
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        is_valid, error_msg = validate_name(data['last_name'], 'Last name')
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        is_valid, error_msg = validate_email(data['email'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Auto-generate staff_id
        school_id = int(data['school_id'])
        staff_id = generate_staff_id(school_id)
        
        # Check if email already has a user account
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already in use'}), 400
        
        # Generate unique username and password
        username = generate_username(data['first_name'], data['last_name'], staff_id)
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
            school_id=school_id,
            staff_id=staff_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            qualification=data.get('qualification'),
            specialization=data.get('specialization'),
            is_active=data.get('is_active', 'true').lower() == 'true'
        )
        
        db.session.add(teacher)
        db.session.flush()  # Get teacher ID before committing
        
        # Handle photo upload
        if photo_file:
            success, filename, error = save_teacher_photo(photo_file, teacher.id)
            if success:
                teacher.photo_filename = filename
            else:
                current_app.logger.warning(f"Failed to save teacher photo: {error}")
        
        db.session.commit()
        
        # Return teacher info WITH auto-generated credentials
        response = teacher.to_dict()
        response['user_id'] = user.id
        response['auto_generated_credentials'] = {
            'username': username,
            'password': password,
            'staff_id': staff_id,
            'email': data['email'],
            'note': 'These credentials are auto-generated. Teacher should change password on first login.'
        }
        
        # Optional: Send credentials via email if requested
        send_email = data.get('send_email', 'false').lower() == 'true'
        if send_email:
            full_name = f"{data['first_name']} {data['last_name']}"
            email_sent = send_credentials_email(
                recipient_email=data['email'],
                recipient_name=full_name,
                username=username,
                password=password,
                role='teacher'
            )
            response['email_sent'] = email_sent
            if email_sent:
                response['email_message'] = f'Credentials sent to {data["email"]}'
            else:
                response['email_message'] = 'Failed to send credentials email. Check SMTP configuration.'
        
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Teacher creation error: {str(e)}")
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
