"""
Flask application factory for FVS Result Management System
"""
from flask import Flask, jsonify, send_from_directory, render_template_string, request
from flask_cors import CORS
from config import config
from models import db, User
import os

def create_app(config_name=None):
    """Create and configure Flask application"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Get the absolute path to frontend folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_path = os.path.join(current_dir, '..', 'frontend')
    frontend_path = os.path.abspath(frontend_path)
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from routes import school_bp, student_bp, teacher_bp, subject_bp, result_bp, class_bp, academic_bp, auth_bp, parent_bp, analytics_bp, export_bp, photo_bp
    
    app.register_blueprint(auth_bp.auth_bp)
    app.register_blueprint(school_bp.school_bp)
    app.register_blueprint(student_bp.student_bp)
    app.register_blueprint(teacher_bp.teacher_bp)
    app.register_blueprint(subject_bp.subject_bp)
    app.register_blueprint(result_bp.result_bp)
    app.register_blueprint(class_bp.class_bp)
    app.register_blueprint(academic_bp.academic_bp)
    app.register_blueprint(parent_bp.parent_bp)
    app.register_blueprint(analytics_bp.analytics_bp)
    app.register_blueprint(export_bp.export_bp)
    app.register_blueprint(photo_bp.photo_bp)
    
    # Serve frontend files
    @app.route('/')
    def root():
        """Serve login page at root"""
        try:
            return send_from_directory(frontend_path, 'login.html')
        except:
            return jsonify({'error': 'Frontend not found'}), 404
    
    @app.route('/<path:filename>')
    def serve_files(filename):
        """Serve static files from frontend"""
        try:
            file_path = os.path.join(frontend_path, filename)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return send_from_directory(frontend_path, filename)
        except:
            pass
        
        # If file not found and it's an HTML request, serve login.html (SPA fallback)
        if filename.endswith('.html'):
            try:
                return send_from_directory(frontend_path, 'login.html'), 404
            except:
                pass
        
        return jsonify({'error': 'Resource not found'}), 404
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        # Try to serve from frontend for HTML files
        if request.path.endswith('.html'):
            try:
                return send_from_directory(frontend_path, 'login.html')
            except:
                return jsonify({'error': 'Resource not found'}), 404
        # For API routes, return JSON error
        if request.path.startswith('/api'):
            return jsonify({'error': 'Resource not found'}), 404
        # Otherwise try to serve from frontend
        try:
            requested_file = request.path.lstrip('/')
            if os.path.exists(os.path.join(frontend_path, requested_file)):
                return send_from_directory(frontend_path, requested_file)
        except:
            pass
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'message': 'FVS Result Management System running'}), 200
    
    # Create database tables and default admin
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@fvs.edu.ng',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin user created - Username: admin, Password: admin123")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
