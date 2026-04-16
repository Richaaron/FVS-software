"""
Class routes
"""
from flask import Blueprint, request, jsonify
from models import db, StudentClass, Subject
from .auth_utils import require_auth, require_role

class_bp = Blueprint('class', __name__, url_prefix='/api/classes')

@class_bp.route('', methods=['POST'])
@require_role('admin')
def create_class():
    """Create a new class"""
    try:
        data = request.get_json()
        
        required = ['school_id', 'name', 'level']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        student_class = StudentClass(
            school_id=data['school_id'],
            name=data['name'],
            level=data['level'],
            arm=data.get('arm'),
            form_teacher_id=data.get('form_teacher_id')
        )
        
        db.session.add(student_class)
        db.session.commit()
        
        return jsonify(student_class.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_bp.route('', methods=['GET'])
@require_auth
def get_classes():
    """Get all classes"""
    try:
        school_id = request.args.get('school_id', type=int)
        level = request.args.get('level')
        
        query = StudentClass.query
        if school_id:
            query = query.filter_by(school_id=school_id)
        if level:
            query = query.filter_by(level=level)
        
        classes = query.all()
        return jsonify([cls.to_dict() for cls in classes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@class_bp.route('/<int:class_id>', methods=['GET'])
@require_auth
def get_class(class_id):
    """Get class details"""
    try:
        student_class = StudentClass.query.get(class_id)
        if not student_class:
            return jsonify({'error': 'Class not found'}), 404
        
        class_data = student_class.to_dict()
        class_data['students'] = [s.to_dict() for s in student_class.students]
        class_data['subjects'] = [s.to_dict() for s in student_class.subjects]
        
        return jsonify(class_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@class_bp.route('/<int:class_id>/subjects', methods=['POST'])
@require_role('admin')
def add_subject_to_class(class_id):
    """Add subject to class"""
    try:
        student_class = StudentClass.query.get(class_id)
        if not student_class:
            return jsonify({'error': 'Class not found'}), 404
        
        data = request.get_json()
        subject_id = data.get('subject_id')
        
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        if subject not in student_class.subjects:
            student_class.subjects.append(subject)
            db.session.commit()
        
        return jsonify(student_class.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@class_bp.route('/<int:class_id>', methods=['PUT'])
@require_role('admin')
def update_class(class_id):
    """Update class"""
    try:
        student_class = StudentClass.query.get(class_id)
        if not student_class:
            return jsonify({'error': 'Class not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            student_class.name = data['name']
        if 'level' in data:
            student_class.level = data['level']
        if 'arm' in data:
            student_class.arm = data['arm']
        if 'form_teacher_id' in data:
            student_class.form_teacher_id = data['form_teacher_id']
        
        db.session.commit()
        return jsonify(student_class.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
