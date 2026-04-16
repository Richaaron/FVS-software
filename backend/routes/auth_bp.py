"""
Authentication routes
"""
from flask import Blueprint, request, jsonify, current_app
from models import db, User, Teacher, Parent, Student
from datetime import datetime, timedelta
import jwt
import os
import secrets
import hashlib
from .validation_utils import validate_email, validate_username, validate_password
from .audit_logger import log_login, log_password_change
from .email_utils import send_password_reset_email, send_credentials_email

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
TOKEN_EXPIRY_HOURS = 24

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        required = ['username', 'email', 'password', 'role']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields: username, email, password, role'}), 400
        
        # Validate inputs
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        role = data['role'].strip().lower()
        
        # Validate email
        is_valid, error_msg = validate_email(email)
        if not is_valid:
            return jsonify({'error': f'Email validation: {error_msg}'}), 400
        
        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return jsonify({'error': f'Username validation: {error_msg}'}), 400
        
        # Validate password strength
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': f'Password validation: {error_msg}'}), 400
        
        if role not in ['admin', 'teacher', 'parent']:
            return jsonify({'error': 'Invalid role. Must be: admin, teacher, or parent'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create new user
        user = User(
            username=username,
            email=email,
            role=role,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing username or password'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            log_login(0, username, success=False)
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            log_login(user.id, username, success=False)
            return jsonify({'error': 'User account is inactive'}), 403
        
        # Log successful login
        log_login(user.id, username, success=True)
        
        # Generate JWT token
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        
        # Get additional info based on role
        user_info = user.to_dict()
        
        if user.role == 'teacher' and user.teacher:
            user_info['teacher_id'] = user.teacher.id
            user_info['classes'] = [c.id for c in user.teacher.subjects_taught]
        
        if user.role == 'parent' and user.parent:
            user_info['parent_id'] = user.parent.id
            user_info['children'] = [c.id for c in user.parent.children]
        
        return jsonify({
            'token': token,
            'user': user_info
        }), 200
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """Verify JWT token"""
    try:
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        return jsonify(user.to_dict()), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    try:
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        
        # Verify token
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data.get('old_password') or not data.get('new_password'):
            return jsonify({'error': 'Missing old or new password'}), 400
        
        if not user.check_password(data['old_password']):
            return jsonify({'error': 'Incorrect old password'}), 401
        
        user.set_password(data['new_password'])
        db.session.commit()
        
        log_password_change(user.id)
        
        return jsonify({'message': 'Password changed successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset email"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].strip().lower()
        
        # Validate email
        is_valid, error_msg = validate_email(email)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # For security, don't reveal if email exists
            return jsonify({'message': 'If email exists, reset link has been sent'}), 200
        
        # Generate reset token (valid for 1 hour)
        reset_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
        
        # Store token hash and expiry in user (we'll add these fields to User model)
        user.password_reset_token = token_hash
        user.password_reset_expiry = datetime.utcnow() + timedelta(hours=1)
        
        db.session.commit()
        
        # Send reset email
        reset_link = f"{request.host_url.rstrip('/')}/reset-password?token={reset_token}"
        email_sent = send_password_reset_email(user.email, user.username, reset_token, reset_link)
        
        if email_sent:
            return jsonify({'message': 'Password reset link sent to email'}), 200
        else:
            return jsonify({'message': 'Password reset requested (email service unavailable)'}), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({'error': 'An error occurred. Please try again later.'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using reset token"""
    try:
        data = request.get_json()
        
        if not data or not data.get('token') or not data.get('new_password'):
            return jsonify({'error': 'Token and new password are required'}), 400
        
        reset_token = data['token'].strip()
        new_password = data['new_password']
        
        # Validate password strength
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Hash the provided token to compare
        token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
        
        # Find user with matching token
        user = User.query.filter_by(password_reset_token=token_hash).first()
        
        if not user:
            return jsonify({'error': 'Invalid reset token'}), 400
        
        # Check if token is expired
        if user.password_reset_expiry < datetime.utcnow():
            return jsonify({'error': 'Reset token has expired'}), 400
        
        # Reset password
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_expiry = None
        
        db.session.commit()
        
        log_password_change(user.id)
        
        return jsonify({'message': 'Password reset successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({'error': 'An error occurred during password reset'}), 500

@auth_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users (admin only)"""
    try:
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        if payload['role'] != 'admin':
            return jsonify({'error': 'Unauthorized'}), 403
        
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
