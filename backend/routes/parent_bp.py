"""
Parent management routes
"""
from flask import Blueprint, request, jsonify
from models import db, Parent, Student
from routes.auth_utils import require_role, get_current_user_role
import jwt
import os

parent_bp = Blueprint('parent', __name__, url_prefix='/api/parents')

SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

def get_user_from_token():
    """Extract user info from JWT token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None

@parent_bp.route('', methods=['POST'])
@require_role('admin')
def create_parent():
    """Create a new parent (admin only)"""
    try:
        data = request.get_json()
        
        required = ['user_id', 'school_id', 'first_name', 'last_name']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        parent = Parent(
            user_id=data['user_id'],
            school_id=data['school_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            email=data.get('email')
        )
        
        db.session.add(parent)
        db.session.commit()
        
        return jsonify(parent.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@parent_bp.route('/<int:parent_id>', methods=['GET'])
def get_parent(parent_id):
    """Get parent details"""
    try:
        user_payload = get_user_from_token()
        if not user_payload:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Parents can only see their own info
        parent = Parent.query.get(parent_id)
        if not parent:
            return jsonify({'error': 'Parent not found'}), 404
        
        if user_payload['role'] == 'parent' and parent.user_id != user_payload['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        parent_data = parent.to_dict()
        parent_data['children'] = [c.to_dict() for c in parent.children]
        
        return jsonify(parent_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parent_bp.route('/<int:parent_id>/children', methods=['GET'])
def get_parent_children(parent_id):
    """Get all children of a parent"""
    try:
        user_payload = get_user_from_token()
        if not user_payload:
            return jsonify({'error': 'Unauthorized'}), 401
        
        parent = Parent.query.get(parent_id)
        if not parent:
            return jsonify({'error': 'Parent not found'}), 404
        
        # Parents can only see their own children
        if user_payload['role'] == 'parent' and parent.user_id != user_payload['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        children = Student.query.filter_by(parent_id=parent_id).all()
        return jsonify([child.to_dict() for child in children]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parent_bp.route('/<int:parent_id>/update', methods=['PUT'])
def update_parent(parent_id):
    """Update parent information"""
    try:
        user_payload = get_user_from_token()
        if not user_payload:
            return jsonify({'error': 'Unauthorized'}), 401
        
        parent = Parent.query.get(parent_id)
        if not parent:
            return jsonify({'error': 'Parent not found'}), 404
        
        # Parents can only update their own info
        if user_payload['role'] == 'parent' and parent.user_id != user_payload['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if 'first_name' in data:
            parent.first_name = data['first_name']
        if 'last_name' in data:
            parent.last_name = data['last_name']
        if 'phone' in data:
            parent.phone = data['phone']
        if 'email' in data:
            parent.email = data['email']
        
        db.session.commit()
        return jsonify(parent.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
