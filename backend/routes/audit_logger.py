"""
Audit logging utilities for the FVS Software backend
Tracks all administrative actions for compliance and debugging
"""

import os
import json
from datetime import datetime
from flask import request, current_app
from models import db

# Create audit log file if it doesn't exist
AUDIT_LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
AUDIT_LOG_FILE = os.path.join(AUDIT_LOG_DIR, 'audit.log')

if not os.path.exists(AUDIT_LOG_DIR):
    os.makedirs(AUDIT_LOG_DIR)

def log_action(user_id: int, action: str, resource_type: str, resource_id: int = None, 
               details: dict = None, status: str = 'success') -> None:
    """
    Log an administrative action
    
    Args:
        user_id: ID of the user performing the action
        action: Action performed (CREATE, UPDATE, DELETE, LOGIN, etc.)
        resource_type: Type of resource affected (User, Student, Teacher, Result, etc.)
        resource_id: ID of the resource affected (optional)
        details: Additional details as dictionary (optional)
        status: Status of the action (success, failure)
    """
    try:
        timestamp = datetime.now().isoformat()
        ip_address = request.remote_addr if request else 'unknown'
        
        log_entry = {
            'timestamp': timestamp,
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'ip_address': ip_address,
            'status': status,
            'details': details or {}
        }
        
        # Write to file
        with open(AUDIT_LOG_FILE, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Optional: Store in database for searchability
        # Uncomment if you add an AuditLog model
        # audit_record = AuditLog(
        #     user_id=user_id,
        #     action=action,
        #     resource_type=resource_type,
        #     resource_id=resource_id,
        #     ip_address=ip_address,
        #     status=status,
        #     details=json.dumps(details or {}),
        #     timestamp=datetime.now()
        # )
        # db.session.add(audit_record)
        # db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Failed to log action: {str(e)}")

def log_login(user_id: int, username: str, success: bool = True) -> None:
    """Log login attempts"""
    log_action(
        user_id=user_id,
        action='LOGIN',
        resource_type='User',
        resource_id=user_id,
        details={'username': username},
        status='success' if success else 'failure'
    )

def log_password_change(user_id: int) -> None:
    """Log password changes"""
    log_action(
        user_id=user_id,
        action='PASSWORD_CHANGE',
        resource_type='User',
        resource_id=user_id
    )

def log_teacher_creation(user_id: int, teacher_id: int, teacher_name: str) -> None:
    """Log teacher creation"""
    log_action(
        user_id=user_id,
        action='CREATE',
        resource_type='Teacher',
        resource_id=teacher_id,
        details={'name': teacher_name}
    )

def log_student_creation(user_id: int, student_id: int, student_name: str) -> None:
    """Log student creation"""
    log_action(
        user_id=user_id,
        action='CREATE',
        resource_type='Student',
        resource_id=student_id,
        details={'name': student_name}
    )

def log_result_modification(user_id: int, result_id: int, action: str = 'UPDATE') -> None:
    """Log result creation or modification"""
    log_action(
        user_id=user_id,
        action=action,
        resource_type='Result',
        resource_id=result_id
    )

def log_deletion(user_id: int, resource_type: str, resource_id: int) -> None:
    """Log deletion of any resource"""
    log_action(
        user_id=user_id,
        action='DELETE',
        resource_type=resource_type,
        resource_id=resource_id
    )

def get_audit_logs(limit: int = 100) -> list:
    """
    Retrieve recent audit logs
    
    Args:
        limit: Maximum number of logs to retrieve
    
    Returns:
        List of audit log entries
    """
    try:
        logs = []
        with open(AUDIT_LOG_FILE, 'r') as f:
            lines = f.readlines()[-limit:]
            for line in lines:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return logs
    except FileNotFoundError:
        return []

def get_user_activity(user_id: int, limit: int = 50) -> list:
    """Get activity logs for a specific user"""
    try:
        logs = []
        with open(AUDIT_LOG_FILE, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry['user_id'] == user_id:
                        logs.append(entry)
                except json.JSONDecodeError:
                    continue
        return logs[-limit:]
    except FileNotFoundError:
        return []
