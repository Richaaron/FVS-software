"""
Analytics and statistics endpoints
Provides dashboard statistics and performance metrics
"""

from flask import Blueprint, request, jsonify, current_app
from .auth_utils import require_auth, require_role, get_current_user_id
from .analytics_utils import (
    get_dashboard_stats, 
    get_student_performance, 
    get_class_performance,
    get_grade_distribution
)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/dashboard', methods=['GET'])
@require_auth
@require_role('admin')
def get_dashboard_analytics():
    """Get dashboard statistics (admin only)"""
    try:
        school_id = request.args.get('school_id', type=int)
        
        stats = get_dashboard_stats(school_id)
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Analytics error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/student/<int:student_id>', methods=['GET'])
@require_auth
def get_student_stats(student_id: int):
    """Get performance statistics for a specific student"""
    try:
        performance = get_student_performance(student_id)
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'data': performance
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Analytics error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/class/<int:class_id>', methods=['GET'])
@require_auth
@require_role('admin', 'teacher')
def get_class_stats(class_id: int):
    """Get performance statistics for a specific class"""
    try:
        performance = get_class_performance(class_id)
        
        return jsonify({
            'success': True,
            'class_id': class_id,
            'data': performance
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Analytics error: {str(e)}")
        return jsonify({'error': str(e)}), 500
