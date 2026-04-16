"""
Subject routes
"""
from flask import Blueprint, request, jsonify
from models import db, Subject
from .auth_utils import require_auth, require_role

subject_bp = Blueprint('subject', __name__, url_prefix='/api/subjects')

@subject_bp.route('', methods=['POST'])
@require_role('admin')
def create_subject():
    """Create a new subject"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Subject name is required'}), 400
        
        subject = Subject(
            school_id=data['school_id'],
            teacher_id=data.get('teacher_id'),
            name=data['name'],
            code=data.get('code'),
            description=data.get('description'),
            credit_hours=data.get('credit_hours', 0),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(subject)
        db.session.commit()
        
        return jsonify(subject.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subject_bp.route('', methods=['GET'])
@require_auth
def get_subjects():
    """Get all subjects"""
    try:
        school_id = request.args.get('school_id', type=int)
        
        query = Subject.query
        if school_id:
            query = query.filter_by(school_id=school_id)
        
        subjects = query.all()
        return jsonify([subject.to_dict() for subject in subjects]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subject_bp.route('/<int:subject_id>', methods=['GET'])
@require_auth
def get_subject(subject_id):
    """Get subject details"""
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        return jsonify(subject.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subject_bp.route('/<int:subject_id>', methods=['PUT'])
@require_role('admin')
def update_subject(subject_id):
    """Update subject"""
    try:
        subject = Subject.query.get(subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            subject.name = data['name']
        if 'code' in data:
            subject.code = data['code']
        if 'description' in data:
            subject.description = data['description']
        if 'teacher_id' in data:
            subject.teacher_id = data['teacher_id']
        if 'credit_hours' in data:
            subject.credit_hours = data['credit_hours']
        if 'is_active' in data:
            subject.is_active = data['is_active']
        
        db.session.commit()
        return jsonify(subject.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
