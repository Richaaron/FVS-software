"""
Analytics and statistics utilities for the FVS Software backend
Generates dashboard statistics and KPIs
"""

from models import db, Student, Teacher, Parent, Result, School, User
from sqlalchemy import func
from datetime import datetime, timedelta

def get_dashboard_stats(school_id: int = None) -> dict:
    """
    Get comprehensive dashboard statistics
    
    Args:
        school_id: Optional school ID to filter stats
    
    Returns:
        Dictionary containing various statistics
    """
    try:
        stats = {
            'timestamp': datetime.now().isoformat(),
            'school_id': school_id
        }
        
        # Build base queries
        student_query = Student.query
        teacher_query = Teacher.query
        result_query = Result.query
        user_query = User.query
        
        # Filter by school if provided
        if school_id:
            student_query = student_query.filter_by(school_id=school_id)
            teacher_query = teacher_query.filter_by(school_id=school_id)
            user_query = user_query.filter_by(role='admin')  # Admin is school-agnostic
        
        # Total counts
        stats['total_students'] = student_query.count()
        stats['total_teachers'] = teacher_query.count()
        stats['total_admins'] = user_query.filter_by(role='admin').count()
        stats['total_parents'] = user_query.filter_by(role='parent').count()
        stats['total_schools'] = School.query.count() if not school_id else 1
        
        # Active/Inactive counts
        stats['active_students'] = student_query.filter_by(is_active=True).count()
        stats['inactive_students'] = student_query.filter_by(is_active=False).count()
        stats['active_teachers'] = teacher_query.filter_by(is_active=True).count()
        stats['inactive_teachers'] = teacher_query.filter_by(is_active=False).count()
        
        # Result statistics
        if school_id:
            result_query = result_query.join(Student).filter(Student.school_id == school_id)
        
        total_results = result_query.count()
        stats['total_results'] = total_results
        
        # Grade distribution
        stats['grade_distribution'] = get_grade_distribution(result_query)
        
        # Average scores
        avg_score = db.session.query(func.avg(Result.total_score)).scalar()
        stats['average_score'] = float(avg_score) if avg_score else 0
        
        # Highest and lowest scores
        highest = db.session.query(func.max(Result.total_score)).scalar()
        lowest = db.session.query(func.min(Result.total_score)).scalar()
        stats['highest_score'] = float(highest) if highest else 0
        stats['lowest_score'] = float(lowest) if lowest else 0
        
        # Results by class
        stats['results_by_class'] = get_results_by_class(school_id)
        
        # Results by subject (top 5)
        stats['top_subjects'] = get_top_performing_subjects(school_id, limit=5)
        stats['bottom_subjects'] = get_bottom_performing_subjects(school_id, limit=5)
        
        # Recent activity
        stats['recent_results'] = get_recent_results(school_id, limit=10)
        
        return stats
    
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def get_grade_distribution(result_query=None) -> dict:
    """
    Get distribution of grades (A, B, C, D, F)
    
    Args:
        result_query: Optional filtered Result query
    
    Returns:
        Dictionary with grade counts and percentages
    """
    if result_query is None:
        result_query = Result.query
    
    total = result_query.count()
    
    if total == 0:
        return {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    
    grades = {}
    for grade in ['A', 'B', 'C', 'D', 'F']:
        count = result_query.filter_by(grade=grade).count()
        grades[grade] = {
            'count': count,
            'percentage': round((count / total) * 100, 2) if total > 0 else 0
        }
    
    return grades

def get_results_by_class(school_id: int = None) -> dict:
    """
    Get results statistics by class
    
    Args:
        school_id: Optional school ID filter
    
    Returns:
        Dictionary with class-wise statistics
    """
    try:
        query = db.session.query(
            Result.class_id,
            db.func.count(Result.id).label('total_results'),
            db.func.avg(Result.total_score).label('avg_score')
        ).group_by(Result.class_id)
        
        if school_id:
            query = query.join(Student).filter(Student.school_id == school_id)
        
        results = {}
        for row in query.all():
            results[str(row[0])] = {
                'total_results': row[1],
                'average_score': round(float(row[2]), 2) if row[2] else 0
            }
        
        return results
    except Exception as e:
        return {}

def get_top_performing_subjects(school_id: int = None, limit: int = 5) -> list:
    """
    Get top performing subjects by average score
    
    Args:
        school_id: Optional school ID filter
        limit: Number of subjects to return
    
    Returns:
        List of top performing subjects
    """
    try:
        query = db.session.query(
            Result.subject_id,
            db.func.count(Result.id).label('count'),
            db.func.avg(Result.total_score).label('avg_score')
        ).group_by(Result.subject_id).order_by(db.func.avg(Result.total_score).desc())
        
        if school_id:
            query = query.join(Student).filter(Student.school_id == school_id)
        
        subjects = []
        for row in query.limit(limit).all():
            subjects.append({
                'subject_id': row[0],
                'count': row[1],
                'average_score': round(float(row[2]), 2) if row[2] else 0
            })
        
        return subjects
    except Exception as e:
        return []

def get_bottom_performing_subjects(school_id: int = None, limit: int = 5) -> list:
    """
    Get bottom performing subjects by average score
    
    Args:
        school_id: Optional school ID filter
        limit: Number of subjects to return
    
    Returns:
        List of bottom performing subjects
    """
    try:
        query = db.session.query(
            Result.subject_id,
            db.func.count(Result.id).label('count'),
            db.func.avg(Result.total_score).label('avg_score')
        ).group_by(Result.subject_id).order_by(db.func.avg(Result.total_score).asc())
        
        if school_id:
            query = query.join(Student).filter(Student.school_id == school_id)
        
        subjects = []
        for row in query.limit(limit).all():
            subjects.append({
                'subject_id': row[0],
                'count': row[1],
                'average_score': round(float(row[2]), 2) if row[2] else 0
            })
        
        return subjects
    except Exception as e:
        return []

def get_recent_results(school_id: int = None, limit: int = 10) -> list:
    """
    Get most recently added results
    
    Args:
        school_id: Optional school ID filter
        limit: Number of results to return
    
    Returns:
        List of recent results
    """
    try:
        query = Result.query.order_by(Result.created_at.desc())
        
        if school_id:
            query = query.join(Student).filter(Student.school_id == school_id)
        
        results = []
        for result in query.limit(limit).all():
            results.append({
                'id': result.id,
                'student_name': result.student.first_name + ' ' + result.student.last_name if result.student else 'N/A',
                'subject_id': result.subject_id,
                'total_score': result.total_score,
                'grade': result.grade,
                'created_at': result.created_at.isoformat()
            })
        
        return results
    except Exception as e:
        return []

def get_student_performance(student_id: int) -> dict:
    """
    Get performance statistics for a specific student
    
    Args:
        student_id: Student ID
    
    Returns:
        Dictionary with student performance data
    """
    try:
        results = Result.query.filter_by(student_id=student_id).all()
        
        if not results:
            return {'total_results': 0, 'average_score': 0, 'grades': {}}
        
        total_results = len(results)
        average_score = sum([r.total_score for r in results]) / total_results
        
        grades = {}
        for result in results:
            if result.grade not in grades:
                grades[result.grade] = 0
            grades[result.grade] += 1
        
        return {
            'total_results': total_results,
            'average_score': round(average_score, 2),
            'grades': grades,
            'highest_score': max([r.total_score for r in results]),
            'lowest_score': min([r.total_score for r in results])
        }
    
    except Exception as e:
        return {'error': str(e)}

def get_class_performance(class_id: int) -> dict:
    """
    Get performance statistics for a specific class
    
    Args:
        class_id: Class ID
    
    Returns:
        Dictionary with class performance data
    """
    try:
        results = Result.query.filter_by(class_id=class_id).all()
        
        if not results:
            return {'total_results': 0, 'student_count': 0, 'average_score': 0}
        
        students = set([r.student_id for r in results])
        total_results = len(results)
        average_score = sum([r.total_score for r in results]) / total_results
        
        return {
            'total_results': total_results,
            'student_count': len(students),
            'average_score': round(average_score, 2),
            'grade_distribution': get_grade_distribution(Result.query.filter_by(class_id=class_id))
        }
    
    except Exception as e:
        return {'error': str(e)}
