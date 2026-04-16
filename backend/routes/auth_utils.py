"""
Authorization utilities
"""
from functools import wraps
from flask import request, jsonify
import jwt
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

def get_token_from_request():
    """Extract JWT token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None
    
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    
    return auth_header

def verify_token_and_get_user():
    """Verify token and return user info"""
    token = get_token_from_request()
    
    if not token:
        return None, None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, ('Token expired', 401)
    except jwt.InvalidTokenError:
        return None, ('Invalid token', 401)
    except Exception as e:
        return None, (str(e), 500)

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload, error = verify_token_and_get_user()
        
        if error:
            return jsonify({'error': error[0]}), error[1]
        
        if not payload:
            return jsonify({'error': 'Unauthorized'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(*roles):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            payload, error = verify_token_and_get_user()
            
            if error:
                return jsonify({'error': error[0]}), error[1]
            
            if not payload:
                return jsonify({'error': 'Unauthorized'}), 401
            
            if payload['role'] not in roles:
                return jsonify({'error': 'Forbidden: Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

def get_current_user_id():
    """Get current user ID from token"""
    payload, _ = verify_token_and_get_user()
    return payload['user_id'] if payload else None

def get_current_user_role():
    """Get current user role from token"""
    payload, _ = verify_token_and_get_user()
    return payload['role'] if payload else None
