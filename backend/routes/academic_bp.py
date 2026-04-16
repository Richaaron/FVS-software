"""
Academic session and term routes
"""
from flask import Blueprint, request, jsonify
from models import db, AcademicSession, Term
from datetime import datetime
from .auth_utils import require_auth, require_role
from .teacher_utils import create_subjects_for_school, get_nigerian_subjects

academic_bp = Blueprint('academic', __name__, url_prefix='/api/academic')

@academic_bp.route('/sessions', methods=['POST'])
@require_role('admin')
def create_session():
    """Create a new academic session"""
    try:
        data = request.get_json()
        
        required = ['school_id', 'session_name', 'start_date', 'end_date']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        session = AcademicSession(
            school_id=data['school_id'],
            session_name=data['session_name'],
            start_date=datetime.fromisoformat(data['start_date']).date(),
            end_date=datetime.fromisoformat(data['end_date']).date(),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify(session.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@academic_bp.route('/sessions', methods=['GET'])
@require_auth
def get_sessions():
    """Get academic sessions"""
    try:
        school_id = request.args.get('school_id', type=int)
        
        query = AcademicSession.query
        if school_id:
            query = query.filter_by(school_id=school_id)
        
        sessions = query.all()
        return jsonify([s.to_dict() for s in sessions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@academic_bp.route('/terms', methods=['POST'])
@require_role('admin')
def create_term():
    """Create a new term"""
    try:
        data = request.get_json()
        
        required = ['academic_session_id', 'term_number', 'start_date', 'end_date']
        if not all(k in data for k in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        term = Term(
            academic_session_id=data['academic_session_id'],
            term_number=data['term_number'],
            start_date=datetime.fromisoformat(data['start_date']).date(),
            end_date=datetime.fromisoformat(data['end_date']).date()
        )
        
        db.session.add(term)
        db.session.commit()
        
        return jsonify(term.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@academic_bp.route('/terms', methods=['GET'])
@require_auth
def get_terms():
    """Get terms"""
    try:
        academic_session_id = request.args.get('academic_session_id', type=int)
        
        query = Term.query
        if academic_session_id:
            query = query.filter_by(academic_session_id=academic_session_id)
        
        terms = query.all()
        return jsonify([t.to_dict() for t in terms]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@academic_bp.route('/subjects/initialize', methods=['POST'])
@require_role('admin')
def initialize_nigerian_subjects():
    """
    Initialize all Nigerian school subjects for a school
    Request body: {
        "school_id": 1,
        "levels": ["primary_1_3", "primary_4_6", "jss_1_3", "sss_1_3"]  // optional, defaults to all
    }
    """
    try:
        data = request.get_json()
        
        if 'school_id' not in data:
            return jsonify({'error': 'school_id is required'}), 400
        
        school_id = data['school_id']
        levels = data.get('levels', None)  # None means all levels
        
        result = create_subjects_for_school(school_id, levels)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f"Successfully created {result['subjects_created']} Nigerian school subjects",
                'subjects_created': result['subjects_created'],
                'subjects': result['subjects']
            }), 201
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@academic_bp.route('/subjects/levels', methods=['GET'])
@require_auth
def get_nigerian_subject_levels():
    """Get all available Nigerian school subject levels and their subjects"""
    try:
        levels = get_nigerian_subjects()
        return jsonify({
            'success': True,
            'levels': {
                'pre_nursery': {
                    'name': 'Pre-Nursery',
                    'subjects': levels['pre_nursery']
                },
                'nursery': {
                    'name': 'Nursery',
                    'subjects': levels['nursery']
                },
                'primary_1_3': {
                    'name': 'Primary 1-3',
                    'subjects': levels['primary_1_3']
                },
                'primary_4_6': {
                    'name': 'Primary 4-6',
                    'subjects': levels['primary_4_6']
                },
                'jss_1_3': {
                    'name': 'JSS 1-3 (Junior Secondary)',
                    'subjects': levels['jss_1_3']
                },
                'sss_1_3': {
                    'name': 'SSS 1-3 (Senior Secondary)',
                    'subjects': levels['sss_1_3']
                }
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
