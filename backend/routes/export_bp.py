"""
Data export endpoints for CSV generation
Allows admins and teachers to export data
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from .auth_utils import require_auth, require_role
from .export_utils import (
    export_students_to_csv,
    export_teachers_to_csv, 
    export_results_to_csv,
    export_subjects_to_csv,
    get_csv_filename
)
from models import db, Student, Teacher, Subject, Result
import io

export_bp = Blueprint('export', __name__, url_prefix='/api/export')

@export_bp.route('/students', methods=['GET'])
@require_auth
@require_role('admin', 'teacher')
def export_students():
    """Export students data to CSV"""
    try:
        school_id = request.args.get('school_id', type=int)
        
        # Get students
        query = Student.query
        if school_id:
            query = query.filter_by(school_id=school_id)
        
        students = query.all()
        students_data = []
        
        for student in students:
            students_data.append({
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'phone': student.phone,
                'date_of_birth': student.date_of_birth,
                'gender': student.gender,
                'registration_number': student.registration_number,
                'class_name': student.student_class.name if student.student_class else '',
                'school_name': student.school.name if student.school else '',
                'is_active': student.is_active
            })
        
        csv_buffer = export_students_to_csv(students_data)
        
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=get_csv_filename('students')
        )
    
    except Exception as e:
        current_app.logger.error(f"Export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@export_bp.route('/teachers', methods=['GET'])
@require_auth
@require_role('admin')
def export_teachers():
    """Export teachers data to CSV"""
    try:
        school_id = request.args.get('school_id', type=int)
        
        # Get teachers
        query = Teacher.query.join(db.User)
        if school_id:
            query = query.filter(Teacher.school_id == school_id)
        
        teachers = query.all()
        teachers_data = []
        
        for teacher in teachers:
            teachers_data.append({
                'staff_id': teacher.staff_id,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'email': teacher.email,
                'phone': teacher.phone,
                'qualification': teacher.qualification,
                'specialization': teacher.specialization,
                'username': teacher.user.username if teacher.user else '',
                'school_name': teacher.school.name if teacher.school else '',
                'is_active': teacher.is_active
            })
        
        csv_buffer = export_teachers_to_csv(teachers_data)
        
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=get_csv_filename('teachers')
        )
    
    except Exception as e:
        current_app.logger.error(f"Export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@export_bp.route('/results', methods=['GET'])
@require_auth
@require_role('admin', 'teacher')
def export_results():
    """Export results data to CSV"""
    try:
        school_id = request.args.get('school_id', type=int)
        class_id = request.args.get('class_id', type=int)
        term_id = request.args.get('term_id', type=int)
        
        # Get results
        query = Result.query
        
        if school_id:
            query = query.join(Student).filter(Student.school_id == school_id)
        if class_id:
            query = query.filter(Result.class_id == class_id)
        if term_id:
            query = query.filter(Result.term_id == term_id)
        
        results = query.all()
        results_data = []
        
        for result in results:
            results_data.append({
                'student_name': f"{result.student.first_name} {result.student.last_name}" if result.student else '',
                'registration_number': result.student.registration_number if result.student else '',
                'class_name': result.student_class.name if result.student_class else '',
                'subject_name': result.subject.name if result.subject else '',
                'continuous_assessment': result.continuous_assessment,
                'assignment': result.assignment,
                'exam_score': result.exam_score,
                'total_score': result.total_score,
                'grade': result.grade,
                'remarks': result.remarks,
                'term': result.term.term_number if result.term else '',
                'academic_session': result.academic_session.session_name if result.academic_session else ''
            })
        
        csv_buffer = export_results_to_csv(results_data)
        
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=get_csv_filename('results')
        )
    
    except Exception as e:
        current_app.logger.error(f"Export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@export_bp.route('/subjects', methods=['GET'])
@require_auth
@require_role('admin', 'teacher')
def export_subjects():
    """Export subjects data to CSV"""
    try:
        school_id = request.args.get('school_id', type=int)
        
        # Get subjects
        query = Subject.query
        if school_id:
            query = query.filter_by(school_id=school_id)
        
        subjects = query.all()
        subjects_data = []
        
        for subject in subjects:
            subjects_data.append({
                'id': subject.id,
                'name': subject.name,
                'code': subject.code,
                'description': subject.description,
                'school_name': subject.school.name if subject.school else '',
                'created_at': subject.created_at
            })
        
        csv_buffer = export_subjects_to_csv(subjects_data)
        
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=get_csv_filename('subjects')
        )
    
    except Exception as e:
        current_app.logger.error(f"Export error: {str(e)}")
        return jsonify({'error': str(e)}), 500
