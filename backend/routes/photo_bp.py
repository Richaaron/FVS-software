"""
Photo/Image endpoints for serving student and teacher photos
"""

from flask import Blueprint, send_from_directory, jsonify, current_app
import os

photo_bp = Blueprint('photos', __name__, url_prefix='/api/photos')

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')

@photo_bp.route('/student/<filename>', methods=['GET'])
def get_student_photo(filename):
    """Get student photo"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, 'students', filename)
        if os.path.exists(filepath):
            return send_from_directory(os.path.join(UPLOAD_FOLDER, 'students'), filename)
        return jsonify({'error': 'Photo not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error serving student photo: {str(e)}")
        return jsonify({'error': 'Error retrieving photo'}), 500

@photo_bp.route('/teacher/<filename>', methods=['GET'])
def get_teacher_photo(filename):
    """Get teacher photo"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, 'teachers', filename)
        if os.path.exists(filepath):
            return send_from_directory(os.path.join(UPLOAD_FOLDER, 'teachers'), filename)
        return jsonify({'error': 'Photo not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error serving teacher photo: {str(e)}")
        return jsonify({'error': 'Error retrieving photo'}), 500
