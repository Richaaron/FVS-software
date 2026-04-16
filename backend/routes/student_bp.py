"""
Student routes
"""
from flask import Blueprint, request, jsonify
from models import db, Student, StudentClass
from datetime import datetime
from .auth_utils import require_auth, require_role

student_bp = Blueprint('student', __name__, url_prefix='/api/students')

@student_bp.route('', methods=['POST'])
@require_role('admin')
def create_student():
    """Create a new student"""
    try:
        data = request.get_json()
        
        required = ['school_id', 'class_id', 'admission_number', 'first_name', 'last_name']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        student = Student(
            school_id=data['school_id'],
            class_id=data['class_id'],
            admission_number=data['admission_number'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            middle_name=data.get('middle_name'),
            date_of_birth=datetime.fromisoformat(data['date_of_birth']) if data.get('date_of_birth') else None,
            gender=data.get('gender'),
            email=data.get('email'),
            phone=data.get('phone'),
            parent_name=data.get('parent_name'),
            parent_phone=data.get('parent_phone'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify(student.to_dict()), 201
    except Exception as e:
        db.session.rollback()
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
