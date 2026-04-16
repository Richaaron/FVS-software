"""
Email routes for sending results and credentials
"""
from flask import Blueprint, request, jsonify, current_app
from models import db, Result, Student, Teacher, Parent, User, Subject
from .auth_utils import require_auth, require_role
from .email_utils import send_credentials_email, send_result_notification_email

email_bp = Blueprint('email', __name__, url_prefix='/api/email')

@email_bp.route('/send-teacher-credentials/<int:teacher_id>', methods=['POST'])
@require_role('admin')
def send_teacher_credentials(teacher_id):
    """
    Send teacher login credentials via email
    
    Args:
        teacher_id: ID of the teacher
        
    POST body (optional):
        {
            "username": "generated_username",
            "password": "generated_password",
            "force_resend": true
        }
    """
    try:
        teacher = Teacher.query.get(teacher_id)
        if not teacher:
            return jsonify({'error': 'Teacher not found'}), 404
        
        user = User.query.get(teacher.user_id)
        if not user:
            return jsonify({'error': 'User account not found'}), 404
        
        # Get credentials from request or use existing username
        data = request.get_json() or {}
        username = data.get('username', user.username)
        password = data.get('password')
        
        # If no password provided, ask admin to provide it
        if not password:
            return jsonify({
                'error': 'Password required to send credentials',
                'message': 'Provide password in request body: {"password": "..."}'
            }), 400
        
        # Send email
        full_name = f"{teacher.first_name} {teacher.last_name}"
        success = send_credentials_email(
            recipient_email=teacher.email,
            recipient_name=full_name,
            username=username,
            password=password,
            role='teacher'
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Teacher credentials sent to {teacher.email}',
                'teacher_id': teacher_id,
                'email': teacher.email
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send email',
                'message': 'Check email configuration (SMTP settings)',
                'teacher_id': teacher_id
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Error sending teacher credentials: {str(e)}")
        return jsonify({'error': str(e)}), 500

@email_bp.route('/send-result-to-parent/<int:result_id>', methods=['POST'])
@require_role('admin', 'teacher')
def send_result_to_parent(result_id):
    """
    Send result notification to parent
    
    Args:
        result_id: ID of the result
    """
    try:
        result = Result.query.get(result_id)
        if not result:
            return jsonify({'error': 'Result not found'}), 404
        
        student = Student.query.get(result.student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        parent = Parent.query.get(student.parent_id)
        if not parent:
            return jsonify({'error': 'Parent not found'}), 404
        
        subject = Subject.query.get(result.subject_id)
        if not subject:
            return jsonify({'error': 'Subject not found'}), 404
        
        student_name = f"{student.first_name} {student.last_name}"
        
        # Send email
        success = send_result_notification_email(
            recipient_email=parent.email,
            student_name=student_name,
            subject=subject.name,
            score=result.total_score,
            grade=result.grade
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Result notification sent to {parent.email}',
                'result_id': result_id,
                'student': student_name,
                'subject': subject.name,
                'grade': result.grade,
                'recipient_email': parent.email
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send email',
                'message': 'Check email configuration (SMTP settings)'
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Error sending result notification: {str(e)}")
        return jsonify({'error': str(e)}), 500

@email_bp.route('/send-results-bulk', methods=['POST'])
@require_role('admin', 'teacher')
def send_results_bulk():
    """
    Send multiple results to parents
    
    POST body:
    {
        "result_ids": [1, 2, 3, ...],
        "term_id": 1  (optional, if not provided send all)
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        result_ids = data.get('result_ids', [])
        term_id = data.get('term_id')
        
        # If result_ids not provided but term_id is, get all results for that term
        if not result_ids and term_id:
            results = Result.query.filter_by(term_id=term_id).all()
        elif result_ids:
            results = Result.query.filter(Result.id.in_(result_ids)).all()
        else:
            return jsonify({'error': 'Provide either result_ids or term_id'}), 400
        
        if not results:
            return jsonify({'error': 'No results found'}), 404
        
        sent_count = 0
        failed_results = []
        
        for result in results:
            try:
                student = Student.query.get(result.student_id)
                parent = Parent.query.get(student.parent_id)
                subject = Subject.query.get(result.subject_id)
                
                if not parent or not student or not subject:
                    failed_results.append({
                        'result_id': result.id,
                        'reason': 'Missing student, parent, or subject'
                    })
                    continue
                
                student_name = f"{student.first_name} {student.last_name}"
                success = send_result_notification_email(
                    recipient_email=parent.email,
                    student_name=student_name,
                    subject=subject.name,
                    score=result.total_score,
                    grade=result.grade
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_results.append({
                        'result_id': result.id,
                        'reason': 'Email sending failed'
                    })
            
            except Exception as e:
                failed_results.append({
                    'result_id': result.id,
                    'reason': str(e)
                })
        
        return jsonify({
            'success': True,
            'message': f'Sent {sent_count} of {len(results)} result notifications',
            'sent_count': sent_count,
            'total_count': len(results),
            'failed_results': failed_results
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error in bulk send results: {str(e)}")
        return jsonify({'error': str(e)}), 500

@email_bp.route('/send-teacher-credentials-bulk', methods=['POST'])
@require_role('admin')
def send_teacher_credentials_bulk():
    """
    Send credentials to multiple teachers
    
    POST body:
    {
        "teacher_ids": [1, 2, 3, ...],
        "school_id": 1  (optional, if not provided send all)
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        teacher_ids = data.get('teacher_ids', [])
        school_id = data.get('school_id')
        
        # If teacher_ids not provided but school_id is, get all teachers for that school
        if not teacher_ids and school_id:
            teachers = Teacher.query.filter_by(school_id=school_id).all()
        elif teacher_ids:
            teachers = Teacher.query.filter(Teacher.id.in_(teacher_ids)).all()
        else:
            return jsonify({'error': 'Provide either teacher_ids or school_id'}), 400
        
        if not teachers:
            return jsonify({'error': 'No teachers found'}), 404
        
        sent_count = 0
        failed_teachers = []
        
        for teacher in teachers:
            try:
                user = User.query.get(teacher.user_id)
                if not user:
                    failed_teachers.append({
                        'teacher_id': teacher.id,
                        'reason': 'User account not found'
                    })
                    continue
                
                full_name = f"{teacher.first_name} {teacher.last_name}"
                
                # Note: We can't resend original passwords, so we'd need to generate new one
                # For security, we ask admin to provide password
                success = send_credentials_email(
                    recipient_email=teacher.email,
                    recipient_name=full_name,
                    username=user.username,
                    password=f'[See password in FVS Software dashboard]',
                    role='teacher'
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_teachers.append({
                        'teacher_id': teacher.id,
                        'reason': 'Email sending failed'
                    })
            
            except Exception as e:
                failed_teachers.append({
                    'teacher_id': teacher.id,
                    'reason': str(e)
                })
        
        return jsonify({
            'success': True,
            'message': f'Sent {sent_count} of {len(teachers)} teacher credential emails',
            'sent_count': sent_count,
            'total_count': len(teachers),
            'failed_teachers': failed_teachers,
            'note': 'Passwords should be provided separately for security'
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error in bulk send teacher credentials: {str(e)}")
        return jsonify({'error': str(e)}), 500

@email_bp.route('/config', methods=['GET'])
@require_role('admin')
def get_email_config():
    """
    Get current email configuration (masked for security)
    """
    try:
        import os
        config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'sender_email': os.getenv('SENDER_EMAIL', 'Not configured'),
            'is_configured': bool(os.getenv('SENDER_PASSWORD')),
            'app_url': os.getenv('APP_URL', 'http://localhost:5000')
        }
        
        # Mask email for security
        if config['sender_email'] != 'Not configured':
            parts = config['sender_email'].split('@')
            if len(parts) == 2:
                config['sender_email_masked'] = f"{parts[0][:3]}***@{parts[1]}"
        
        return jsonify(config), 200
    
    except Exception as e:
        current_app.logger.error(f"Error getting email config: {str(e)}")
        return jsonify({'error': str(e)}), 500

@email_bp.route('/test-send', methods=['POST'])
@require_role('admin')
def test_send_email():
    """
    Test email sending capability
    
    POST body:
    {
        "email": "test@example.com"
    }
    """
    try:
        data = request.get_json()
        if not data or not data.get('email'):
            return jsonify({'error': 'Email address required'}), 400
        
        test_email = data['email']
        
        # Simple test email
        from .email_utils import _send_email
        success = _send_email(
            test_email,
            'FVS Software - Email Configuration Test',
            """
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                        <h2 style="color: #0099ff; text-align: center;">FVS Software Email Test</h2>
                        <hr style="border: none; border-top: 2px solid #00d4ff; margin: 20px 0;">
                        
                        <p style="color: #333; font-size: 14px;">
                            This is a test email from FVS Software. If you received this, email configuration is working correctly!
                        </p>
                        
                        <p style="color: #666; font-size: 12px; margin-top: 30px;">
                            © 2026 Folusho Victory Schools
                        </p>
                    </div>
                </body>
            </html>
            """
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Test email sent successfully to {test_email}'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send test email',
                'message': 'Check SMTP configuration and credentials'
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Error in test send: {str(e)}")
        return jsonify({'error': str(e)}), 500
