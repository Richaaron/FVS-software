"""
Result routes with role-based access control
"""
from flask import Blueprint, request, jsonify
from models import db, Result, Student, Subject, Term, Teacher, Parent, User
from sqlalchemy import func
from routes.auth_utils import require_auth, require_role, get_token_from_request
import jwt
import os

result_bp = Blueprint('result', __name__, url_prefix='/api/results')

SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

def get_user_from_token():
    """Extract user info from JWT token"""
    token = get_token_from_request()
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None

@result_bp.route('', methods=['POST'])
@require_role('admin', 'teacher')
def create_result():
    """Create or update a result with CA1, CA2, and Exam scores (admin and teacher only)"""
    try:
        data = request.get_json()
        
        required = ['student_id', 'subject_id', 'term_id']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if result already exists
        result = Result.query.filter_by(
            student_id=data['student_id'],
            subject_id=data['subject_id'],
            term_id=data['term_id']
        ).first()
        
        if not result:
            result = Result(
                student_id=data['student_id'],
                subject_id=data['subject_id'],
                term_id=data['term_id']
            )
        
        # Set assessment scores (1st CA, 2nd CA, Exam)
        result.ca1 = float(data.get('ca1', 0))  # 1st Continuous Assessment (0-10)
        result.ca2 = float(data.get('ca2', 0))  # 2nd Continuous Assessment (0-10)
        result.exam = float(data.get('exam', 0))  # Exam score (0-80)
        
        # Validate score ranges
        if result.ca1 < 0 or result.ca1 > 10:
            return jsonify({'error': 'CA1 must be between 0 and 10'}), 400
        if result.ca2 < 0 or result.ca2 > 10:
            return jsonify({'error': 'CA2 must be between 0 and 10'}), 400
        if result.exam < 0 or result.exam > 80:
            return jsonify({'error': 'Exam must be between 0 and 80'}), 400
        
        # Auto-calculate total, grade, and remarks
        result.calculate_score()
        
        db.session.add(result)
        db.session.commit()
        
        return jsonify(result.to_dict()), 201
    except ValueError:
        return jsonify({'error': 'Invalid score values. Scores must be numeric'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@result_bp.route('', methods=['GET'])
@require_auth
def get_results():
    """Get results with filtering (role-based access)"""
    try:
        user_payload = get_user_from_token()
        if not user_payload:
            return jsonify({'error': 'Unauthorized'}), 401
        
        student_id = request.args.get('student_id', type=int)
        subject_id = request.args.get('subject_id', type=int)
        term_id = request.args.get('term_id', type=int)
        class_id = request.args.get('class_id', type=int)
        
        query = Result.query
        
        # Apply role-based filtering
        if user_payload['role'] == 'parent':
            # Parents can only see their children's results
            parent = Parent.query.filter_by(user_id=user_payload['user_id']).first()
            if not parent:
                return jsonify({'error': 'Parent not found'}), 404
            
            children_ids = [child.id for child in parent.children]
            query = query.filter(Result.student_id.in_(children_ids))
        
        elif user_payload['role'] == 'teacher':
            # Teachers can only see results for their subjects
            teacher = Teacher.query.filter_by(user_id=user_payload['user_id']).first()
            if not teacher:
                return jsonify({'error': 'Teacher not found'}), 404
            
            subject_ids = [subject.id for subject in teacher.subjects_taught]
            query = query.filter(Result.subject_id.in_(subject_ids))
        
        # Apply additional filters
        if student_id:
            query = query.filter_by(student_id=student_id)
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        if term_id:
            query = query.filter_by(term_id=term_id)
        if class_id:
            query = query.join(Student).filter(Student.class_id == class_id)
        
        results = query.all()
        return jsonify([result.to_dict() for result in results]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@result_bp.route('/<int:result_id>', methods=['GET'])
@require_auth
def get_result(result_id):
    """Get result details (with access control)"""
    try:
        user_payload = get_user_from_token()
        if not user_payload:
            return jsonify({'error': 'Unauthorized'}), 401
        
        result = Result.query.get(result_id)
        if not result:
            return jsonify({'error': 'Result not found'}), 404
        
        # Access control
        if user_payload['role'] == 'parent':
            parent = Parent.query.filter_by(user_id=user_payload['user_id']).first()
            if not parent or result.student.parent_id != parent.id:
                return jsonify({'error': 'Unauthorized'}), 403
        
        elif user_payload['role'] == 'teacher':
            teacher = Teacher.query.filter_by(user_id=user_payload['user_id']).first()
            if not teacher or result.subject.teacher_id != teacher.id:
                return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify(result.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@result_bp.route('/<int:result_id>', methods=['PUT'])
@require_role('admin', 'teacher')
def update_result(result_id):
    """Update result with CA1, CA2, and Exam scores (admin and teacher only)"""
    try:
        result = Result.query.get(result_id)
        if not result:
            return jsonify({'error': 'Result not found'}), 404
        
        data = request.get_json()
        
        # Update assessment scores with new field names
        if 'ca1' in data:
            result.ca1 = float(data['ca1'])
            if result.ca1 < 0 or result.ca1 > 10:
                return jsonify({'error': 'CA1 must be between 0 and 10'}), 400
        if 'ca2' in data:
            result.ca2 = float(data['ca2'])
            if result.ca2 < 0 or result.ca2 > 10:
                return jsonify({'error': 'CA2 must be between 0 and 10'}), 400
        if 'exam' in data:
            result.exam = float(data['exam'])
            if result.exam < 0 or result.exam > 80:
                return jsonify({'error': 'Exam must be between 0 and 80'}), 400
        
        # Auto-calculate total, grade, and remarks
        result.calculate_score()
        
        db.session.commit()
        return jsonify(result.to_dict()), 200
    except ValueError:
        return jsonify({'error': 'Invalid score values. Scores must be numeric'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@result_bp.route('/student/<int:student_id>/summary', methods=['GET'])
def get_student_summary(student_id):
    """Get student result summary"""
    try:
        term_id = request.args.get('term_id', type=int)
        
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        query = Result.query.filter_by(student_id=student_id)
        if term_id:
            query = query.filter_by(term_id=term_id)
        
        results = query.all()
        
        if not results:
            return jsonify({'error': 'No results found'}), 404
        
        total_score = sum(r.total_score for r in results)
        average_score = total_score / len(results) if results else 0
        
        summary = {
            'student_id': student_id,
            'student_name': student.to_dict()['full_name'],
            'class': student.class_.name if student.class_ else None,
            'total_subjects': len(results),
            'total_score': total_score,
            'average_score': round(average_score, 2),
            'passed': sum(1 for r in results if r.remarks == 'Pass' or r.remarks != 'Fail'),
            'failed': sum(1 for r in results if r.remarks == 'Fail'),
            'results': [r.to_dict() for r in results]
        }
        
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@result_bp.route('/class/<int:class_id>/ranking', methods=['GET'])
def get_class_ranking(class_id):
    """Get class ranking"""
    try:
        term_id = request.args.get('term_id', type=int)
        
        students = Student.query.filter_by(class_id=class_id).all()
        
        rankings = []
        for student in students:
            query = Result.query.filter_by(student_id=student.id)
            if term_id:
                query = query.filter_by(term_id=term_id)
            
            results = query.all()
            if results:
                average = sum(r.total_score for r in results) / len(results)
                rankings.append({
                    'student_id': student.id,
                    'name': f"{student.first_name} {student.last_name}",
                    'admission_number': student.admission_number,
                    'average_score': round(average, 2),
                    'total_subjects': len(results)
                })
        
        # Sort by average score
        rankings.sort(key=lambda x: x['average_score'], reverse=True)
        
        # Add rank
        for i, ranking in enumerate(rankings):
            ranking['rank'] = i + 1
        
        return jsonify(rankings), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
