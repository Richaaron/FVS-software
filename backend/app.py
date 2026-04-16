"""
Flask application factory for FVS Result Management System
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from models import db, User
import os

def create_app(config_name=None):
    """Create and configure Flask application"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from routes import school_bp, student_bp, teacher_bp, subject_bp, result_bp, class_bp, academic_bp, auth_bp, parent_bp
    
    app.register_blueprint(auth_bp.auth_bp)
    app.register_blueprint(school_bp.school_bp)
    app.register_blueprint(student_bp.student_bp)
    app.register_blueprint(teacher_bp.teacher_bp)
    app.register_blueprint(subject_bp.subject_bp)
    app.register_blueprint(result_bp.result_bp)
    app.register_blueprint(class_bp.class_bp)
    app.register_blueprint(academic_bp.academic_bp)
    app.register_blueprint(parent_bp.parent_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
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
