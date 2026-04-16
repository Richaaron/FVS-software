"""
School routes
"""
from flask import Blueprint, request, jsonify
from models import db, School
from datetime import datetime
from .auth_utils import require_auth, require_role

school_bp = Blueprint('school', __name__, url_prefix='/api/schools')

@school_bp.route('', methods=['POST'])
@require_role('admin')
def create_school():
    """Create a new school"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return jsonify({'error': 'School name is required'}), 400
        
        school = School(
            name=data.get('name'),
            address=data.get('address'),
            principal=data.get('principal'),
            email=data.get('email'),
            phone=data.get('phone'),
            established_year=data.get('established_year')
        )
        
        db.session.add(school)
        db.session.commit()
        
        return jsonify(school.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@school_bp.route('', methods=['GET'])
@require_auth
def get_schools():
    """Get all schools"""
    try:
        schools = School.query.all()
        return jsonify([school.to_dict() for school in schools]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@school_bp.route('/<int:school_id>', methods=['GET'])
@require_auth
def get_school(school_id):
    """Get school details"""
    try:
        school = School.query.get(school_id)
        if not school:
            return jsonify({'error': 'School not found'}), 404
        return jsonify(school.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@school_bp.route('/<int:school_id>', methods=['PUT'])
@require_role('admin')
def update_school(school_id):
    """Update school information"""
    try:
        school = School.query.get(school_id)
        if not school:
            return jsonify({'error': 'School not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            school.name = data['name']
        if 'address' in data:
            school.address = data['address']
        if 'principal' in data:
            school.principal = data['principal']
        if 'email' in data:
            school.email = data['email']
        if 'phone' in data:
            school.phone = data['phone']
        if 'established_year' in data:
            school.established_year = data['established_year']
        
        db.session.commit()
        return jsonify(school.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
