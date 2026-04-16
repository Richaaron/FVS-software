"""
Teacher utilities for auto-generating credentials and managing subjects
"""
import random
import string
from models import db, User, Subject

def generate_username(first_name, last_name, teacher_id):
    """
    Generate a unique username from first and last name
    Format: firstname.lastname.randomnumber
    Example: john.doe.1234
    """
    base_username = f"{first_name.lower()}.{last_name.lower()}"
    random_suffix = ''.join(random.choices(string.digits, k=4))
    username = f"{base_username}.{random_suffix}"
    
    # Check if username already exists, if so, regenerate
    while User.query.filter_by(username=username).first():
        random_suffix = ''.join(random.choices(string.digits, k=4))
        username = f"{base_username}.{random_suffix}"
    
    return username

def generate_password(length=12):
    """
    Generate a secure random password
    Contains uppercase, lowercase, digits, and special characters
    """
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%^&*"
    password = ''.join(random.choices(characters, k=length))
    return password

def get_nigerian_subjects():
    """
    Get all subjects offered in Nigerian schools by class level
    Based on Nigerian curriculum (NCDC, JSS/SSS)
    """
    subjects_by_level = {
        'pre_nursery': [
            'Numeracy', 'Literacy', 'Creative Arts', 'Physical Education', 
            'Social Studies', 'Science', 'Music'
        ],
        'nursery': [
            'Numeracy', 'Literacy', 'Creative Arts', 'Physical Education',
            'Social Studies', 'Science', 'Music', 'Health Education'
        ],
        'primary_1_3': [
            'English Language', 'Mathematics', 'Science', 'Social Studies',
            'Physical Education', 'Art', 'Music', 'Religious Studies',
            'Home Economics', 'National Values'
        ],
        'primary_4_6': [
            'English Language', 'Mathematics', 'Science', 'Social Studies',
            'Physical Education', 'Art', 'Music', 'Religious Studies',
            'Home Economics', 'National Values', 'Computer Studies', 'Civic Education'
        ],
        'jss_1_3': [
            'English Language', 'Mathematics', 'Integrated Science',
            'Social Studies', 'History', 'Geography', 'Civic Education',
            'Physical Education', 'Art', 'Music', 'Computer Studies',
            'Agricultural Science', 'Home Economics', 'Religious Studies',
            'National Values'
        ],
        'sss_1_3': [
            'English Language', 'Mathematics', 'Physics', 'Chemistry',
            'Biology', 'History', 'Geography', 'Economics', 'Civic Education',
            'Government', 'Physical Education', 'Art', 'Music',
            'Computer Studies', 'Agricultural Science', 'Food & Nutrition',
            'Clothing & Textiles', 'Literature in English', 'French',
            'Further Mathematics', 'Hausa', 'Igbo', 'Yoruba', 'Arabic',
            'Islamic Studies', 'Christian Religious Studies', 'Islamic Religious Studies',
            'Law', 'Accounting', 'Business Studies', 'Marketing', 'Technical Drawing'
        ]
    }
    return subjects_by_level

def create_subjects_for_school(school_id, level_keys=None):
    """
    Create all Nigerian school subjects for a school and specific levels
    level_keys: list of keys like ['primary_1_3', 'jss_1_3', 'sss_1_3']
    if None, creates all subjects for all levels
    """
    subjects_data = get_nigerian_subjects()
    
    if level_keys is None:
        level_keys = list(subjects_data.keys())
    
    created_subjects = []
    
    for level in level_keys:
        if level in subjects_data:
            for subject_name in subjects_data[level]:
                # Check if subject already exists for this school and level
                existing = Subject.query.filter_by(
                    school_id=school_id,
                    name=subject_name
                ).first()
                
                if not existing:
                    subject = Subject(
                        school_id=school_id,
                        name=subject_name,
                        description=f"{level.replace('_', ' ').title()} - {subject_name}",
                        is_active=True
                    )
                    db.session.add(subject)
                    created_subjects.append(subject_name)
    
    try:
        db.session.commit()
        return {
            'success': True,
            'subjects_created': len(created_subjects),
            'subjects': created_subjects
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e)
        }
