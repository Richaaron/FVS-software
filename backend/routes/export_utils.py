"""
CSV export utilities for the FVS Software backend
Exports data to CSV format for reports and analysis
"""

import csv
from io import StringIO
from datetime import datetime
from typing import List, Dict, Any

def generate_csv_buffer(data: List[Dict[str, Any]], filename: str = None) -> StringIO:
    """
    Generate CSV content in memory
    
    Args:
        data: List of dictionaries to convert to CSV
        filename: Optional filename for reference
    
    Returns:
        StringIO buffer containing CSV data
    """
    if not data:
        return StringIO()
    
    buffer = StringIO()
    fieldnames = data[0].keys()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(data)
    
    buffer.seek(0)
    return buffer

def export_students_to_csv(students: List[Dict[str, Any]]) -> StringIO:
    """
    Export students data to CSV
    
    Args:
        students: List of student dictionaries
    
    Returns:
        CSV buffer
    """
    csv_data = []
    for student in students:
        csv_data.append({
            'Student ID': student.get('id'),
            'First Name': student.get('first_name'),
            'Last Name': student.get('last_name'),
            'Email': student.get('email'),
            'Phone': student.get('phone'),
            'Date of Birth': student.get('date_of_birth'),
            'Gender': student.get('gender'),
            'Registration Number': student.get('registration_number'),
            'Class': student.get('class_name'),
            'School': student.get('school_name'),
            'Status': 'Active' if student.get('is_active') else 'Inactive'
        })
    
    return generate_csv_buffer(csv_data, 'students')

def export_teachers_to_csv(teachers: List[Dict[str, Any]]) -> StringIO:
    """
    Export teachers data to CSV
    
    Args:
        teachers: List of teacher dictionaries
    
    Returns:
        CSV buffer
    """
    csv_data = []
    for teacher in teachers:
        csv_data.append({
            'Staff ID': teacher.get('staff_id'),
            'First Name': teacher.get('first_name'),
            'Last Name': teacher.get('last_name'),
            'Email': teacher.get('email'),
            'Phone': teacher.get('phone'),
            'Qualification': teacher.get('qualification'),
            'Specialization': teacher.get('specialization'),
            'Username': teacher.get('username'),
            'School': teacher.get('school_name'),
            'Status': 'Active' if teacher.get('is_active') else 'Inactive',
            'Date Hired': teacher.get('date_hired')
        })
    
    return generate_csv_buffer(csv_data, 'teachers')

def export_results_to_csv(results: List[Dict[str, Any]]) -> StringIO:
    """
    Export results data to CSV
    
    Args:
        results: List of result dictionaries
    
    Returns:
        CSV buffer
    """
    csv_data = []
    for result in results:
        csv_data.append({
            'Student Name': result.get('student_name'),
            'Registration Number': result.get('registration_number'),
            'Class': result.get('class_name'),
            'Subject': result.get('subject_name'),
            'Continuous Assessment': result.get('continuous_assessment'),
            'Assignment': result.get('assignment'),
            'Exam Score': result.get('exam_score'),
            'Total Score': result.get('total_score'),
            'Grade': result.get('grade'),
            'Remarks': result.get('remarks'),
            'Term': result.get('term'),
            'Academic Session': result.get('academic_session')
        })
    
    return generate_csv_buffer(csv_data, 'results')

def export_result_by_class_to_csv(results: List[Dict[str, Any]], class_name: str) -> StringIO:
    """
    Export class results with summary statistics
    
    Args:
        results: List of result dictionaries
        class_name: Name of the class
    
    Returns:
        CSV buffer
    """
    csv_data = []
    
    # Group by subject
    by_subject = {}
    for result in results:
        subject = result.get('subject_name', 'Unknown')
        if subject not in by_subject:
            by_subject[subject] = []
        by_subject[subject].append(result)
    
    # Create summary per subject
    for subject, subject_results in by_subject.items():
        if subject_results:
            scores = [r.get('total_score', 0) for r in subject_results if r.get('total_score')]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            csv_data.append({
                'Class': class_name,
                'Subject': subject,
                'Number of Students': len(subject_results),
                'Average Score': f"{avg_score:.2f}",
                'Highest Score': max(scores) if scores else 0,
                'Lowest Score': min(scores) if scores else 0
            })
    
    return generate_csv_buffer(csv_data, f'{class_name}_results')

def export_transcript_to_csv(student_results: List[Dict[str, Any]], student_name: str) -> StringIO:
    """
    Export student transcript (all results)
    
    Args:
        student_results: List of result dictionaries for a student
        student_name: Name of the student
    
    Returns:
        CSV buffer
    """
    csv_data = []
    
    # Sort by academic session and term
    sorted_results = sorted(
        student_results,
        key=lambda x: (x.get('academic_session', ''), x.get('term', ''))
    )
    
    current_session = None
    current_term = None
    session_grades = []
    
    for result in sorted_results:
        session = result.get('academic_session', 'Unknown')
        term = result.get('term', 'Unknown')
        
        # Add result row
        csv_data.append({
            'Academic Session': session,
            'Term': term,
            'Subject': result.get('subject_name'),
            'CA': result.get('continuous_assessment'),
            'Assignment': result.get('assignment'),
            'Exam': result.get('exam_score'),
            'Total': result.get('total_score'),
            'Grade': result.get('grade'),
            'Remarks': result.get('remarks')
        })
        
        # Track for summary
        if session != current_session or term != current_term:
            if session_grades:
                # Add summary row
                grades = [g for g in session_grades if g]
                if grades:
                    csv_data.append({
                        'Academic Session': f'{current_session} - {current_term} SUMMARY',
                        'Term': '',
                        'Subject': '',
                        'CA': '',
                        'Assignment': '',
                        'Exam': '',
                        'Total': f"{sum(session_grades)/len(session_grades):.2f}",
                        'Grade': '',
                        'Remarks': 'Session Average'
                    })
            current_session = session
            current_term = term
            session_grades = []
        
        session_grades.append(result.get('total_score'))
    
    return generate_csv_buffer(csv_data, f'{student_name}_transcript')

def export_subjects_to_csv(subjects: List[Dict[str, Any]]) -> StringIO:
    """
    Export subjects data to CSV
    
    Args:
        subjects: List of subject dictionaries
    
    Returns:
        CSV buffer
    """
    csv_data = []
    for subject in subjects:
        csv_data.append({
            'Subject ID': subject.get('id'),
            'Subject Name': subject.get('name'),
            'Code': subject.get('code'),
            'Description': subject.get('description'),
            'School': subject.get('school_name'),
            'Created Date': subject.get('created_at')
        })
    
    return generate_csv_buffer(csv_data, 'subjects')

def get_csv_filename(data_type: str) -> str:
    """
    Generate appropriate filename for CSV export
    
    Args:
        data_type: Type of data being exported
    
    Returns:
        Filename with timestamp
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'{data_type}_{timestamp}.csv'
