"""
Database models for FVS Result Management System
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    """User authentication model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    password_reset_token = db.Column(db.String(255), nullable=True)  # For forgot password flow
    password_reset_expiry = db.Column(db.DateTime, nullable=True)  # Token expiry time
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, parent
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    teacher = db.relationship('Teacher', backref='user', uselist=False, foreign_keys='Teacher.user_id')
    parent = db.relationship('Parent', backref='user', uselist=False, foreign_keys='Parent.user_id')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Parent(db.Model):
    """Parent/Guardian information"""
    __tablename__ = 'parents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    school = db.relationship('School', backref='parents')
    children = db.relationship('Student', backref='parent', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'phone': self.phone,
            'email': self.email
        }

class School(db.Model):
    """School information"""
    __tablename__ = 'schools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.String(255))
    principal = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    established_year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    students = db.relationship('Student', backref='school', lazy=True, cascade='all, delete-orphan')
    teachers = db.relationship('Teacher', backref='school', lazy=True, cascade='all, delete-orphan')
    subjects = db.relationship('Subject', backref='school', lazy=True, cascade='all, delete-orphan')
    academic_sessions = db.relationship('AcademicSession', backref='school', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'principal': self.principal,
            'email': self.email,
            'phone': self.phone,
            'established_year': self.established_year,
            'created_at': self.created_at.isoformat()
        }


class AcademicSession(db.Model):
    """Academic session (e.g., 2023/2024)"""
    __tablename__ = 'academic_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    session_name = db.Column(db.String(20), nullable=False)  # e.g., "2023/2024"
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    terms = db.relationship('Term', backref='academic_session', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('school_id', 'session_name'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'session_name': self.session_name,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'is_active': self.is_active,
            'terms': [t.to_dict() for t in self.terms]
        }


class Term(db.Model):
    """Term within an academic session"""
    __tablename__ = 'terms'
    
    id = db.Column(db.Integer, primary_key=True)
    academic_session_id = db.Column(db.Integer, db.ForeignKey('academic_sessions.id'), nullable=False)
    term_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    results = db.relationship('Result', backref='term', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('academic_session_id', 'term_number'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'academic_session_id': self.academic_session_id,
            'term_number': self.term_number,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat()
        }


class StudentClass(db.Model):
    """Student class/grade"""
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)  # e.g., "Primary 3", "JSS 2"
    level = db.Column(db.String(50), nullable=False)  # Nursery, Primary, Secondary
    arm = db.Column(db.String(20))  # e.g., "A", "B", "C"
    form_teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    students = db.relationship('Student', backref='class_', lazy=True, cascade='all, delete-orphan')
    subjects = db.relationship('Subject', secondary='class_subjects', backref='classes')
    
    __table_args__ = (db.UniqueConstraint('school_id', 'name', 'arm'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'name': self.name,
            'level': self.level,
            'arm': self.arm,
            'form_teacher_id': self.form_teacher_id,
            'student_count': len(self.students)
        }


class Student(db.Model):
    """Student information"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'))  # Link to parent
    admission_number = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))  # Male, Female
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    parent_name = db.Column(db.String(100))
    parent_phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    results = db.relationship('Result', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'class_id': self.class_id,
            'admission_number': self.admission_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_name': self.middle_name,
            'full_name': f"{self.first_name} {self.middle_name or ''} {self.last_name}".strip(),
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'email': self.email,
            'parent_name': self.parent_name,
            'is_active': self.is_active
        }


class Teacher(db.Model):
    """Teacher information"""
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Link to user for authentication
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    staff_id = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    qualification = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subjects_taught = db.relationship('Subject', backref='teacher', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'staff_id': self.staff_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'email': self.email,
            'specialization': self.specialization,
            'is_active': self.is_active
        }


class Subject(db.Model):
    """Subject/Course"""
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    name = db.Column(db.String(100), nullable=False)  # e.g., Mathematics, English
    code = db.Column(db.String(20))
    description = db.Column(db.Text)
    credit_hours = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    results = db.relationship('Result', backref='subject', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'teacher_id': self.teacher_id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'credit_hours': self.credit_hours,
            'is_active': self.is_active
        }


class Result(db.Model):
    """Student result/grade"""
    __tablename__ = 'results'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'), nullable=False)
    
    # Assessment scores
    continuous_assessment = db.Column(db.Float, default=0)  # e.g., 0-20
    assignment = db.Column(db.Float, default=0)
    exam_score = db.Column(db.Float, default=0)  # e.g., 0-80
    
    total_score = db.Column(db.Float, default=0)  # Calculated
    grade = db.Column(db.String(2))  # A, B, C, D, E, F
    remarks = db.Column(db.String(100))  # Pass, Fail, etc.
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_score(self):
        """Calculate total score based on components"""
        self.total_score = self.continuous_assessment + self.assignment + self.exam_score
        self.assign_grade()
        return self.total_score
    
    def assign_grade(self):
        """Assign grade based on total score"""
        score = self.total_score
        if score >= 90:
            self.grade = 'A'
            self.remarks = 'Excellent'
        elif score >= 80:
            self.grade = 'B'
            self.remarks = 'Very Good'
        elif score >= 70:
            self.grade = 'C'
            self.remarks = 'Good'
        elif score >= 60:
            self.grade = 'D'
            self.remarks = 'Fair'
        elif score >= 50:
            self.grade = 'E'
            self.remarks = 'Pass'
        else:
            self.grade = 'F'
            self.remarks = 'Fail'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.first_name + ' ' + self.student.last_name,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name,
            'term_id': self.term_id,
            'continuous_assessment': self.continuous_assessment,
            'assignment': self.assignment,
            'exam_score': self.exam_score,
            'total_score': self.total_score,
            'grade': self.grade,
            'remarks': self.remarks
        }


# Association table for class and subjects
class_subjects = db.Table(
    'class_subjects',
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'), primary_key=True)
)
