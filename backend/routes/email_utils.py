"""
Email utilities for the FVS Software backend
Handles sending emails for password reset, notifications, etc.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from datetime import datetime
import os

# Email configuration (can be moved to environment variables)
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'noreply@fvssoftware.com')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')

def send_password_reset_email(recipient_email: str, recipient_name: str, reset_token: str, 
                              reset_link: str = None) -> bool:
    """
    Send password reset email
    
    Args:
        recipient_email: Email address to send to
        recipient_name: Name of the recipient
        reset_token: Password reset token
        reset_link: Full reset link (optional, can be constructed here)
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        if not reset_link:
            # Construct the reset link (adjust URL as needed)
            base_url = os.getenv('APP_URL', 'http://localhost:5000')
            reset_link = f"{base_url}/reset-password?token={reset_token}"
        
        subject = "FVS Software - Password Reset Request"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <h2 style="color: #0099ff; text-align: center;">FVS Software</h2>
                    <hr style="border: none; border-top: 2px solid #00d4ff; margin: 20px 0;">
                    
                    <h3 style="color: #333;">Hello {recipient_name},</h3>
                    
                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        We received a request to reset your password for your FVS Software account. 
                        If you did not make this request, you can ignore this email.
                    </p>
                    
                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        To reset your password, click the link below:
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="background-color: #00d4ff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            Reset Password
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 12px;">
                        Or copy and paste this link in your browser:<br>
                        <span style="word-break: break-all; color: #0099ff;">{reset_link}</span>
                    </p>
                    
                    <p style="color: #999; font-size: 12px; margin-top: 30px;">
                        This link will expire in 1 hour.<br>
                        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        © 2026 Folusho Victory Schools. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return _send_email(recipient_email, subject, html_content)
    
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email: {str(e)}")
        return False

def send_credentials_email(recipient_email: str, recipient_name: str, username: str, 
                          password: str, role: str = 'teacher') -> bool:
    """
    Send new user credentials email
    
    Args:
        recipient_email: Email address to send to
        recipient_name: Name of the recipient
        username: Generated username
        password: Generated password
        role: User role (teacher, admin, etc.)
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        subject = f"FVS Software - Your {role.capitalize()} Account Credentials"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <h2 style="color: #0099ff; text-align: center;">FVS Software</h2>
                    <hr style="border: none; border-top: 2px solid #00d4ff; margin: 20px 0;">
                    
                    <h3 style="color: #333;">Welcome {recipient_name}!</h3>
                    
                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        Your {role} account has been created in the FVS Software system. 
                        Your login credentials are provided below.
                    </p>
                    
                    <div style="background-color: #f0f8ff; padding: 20px; border-left: 4px solid #00d4ff; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0; color: #333;"><strong>Username:</strong></p>
                        <p style="margin: 10px 0 20px 0; font-size: 16px; color: #0099ff; font-family: monospace; letter-spacing: 1px;">{username}</p>
                        
                        <p style="margin: 0; color: #333;"><strong>Password:</strong></p>
                        <p style="margin: 10px 0 0 0; font-size: 16px; color: #0099ff; font-family: monospace; letter-spacing: 1px;">{password}</p>
                    </div>
                    
                    <p style="color: #d32f2f; font-size: 13px; font-weight: bold; padding: 15px; background-color: #ffebee; border-radius: 5px;">
                        ⚠️ IMPORTANT: Please change your password immediately upon first login. 
                        Do not share these credentials with anyone.
                    </p>
                    
                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        To access FVS Software:<br>
                        <a href="http://localhost:5000" style="color: #0099ff; text-decoration: none;">Click here to log in</a>
                    </p>
                    
                    <p style="color: #999; font-size: 12px; margin-top: 30px;">
                        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        © 2026 Folusho Victory Schools. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return _send_email(recipient_email, subject, html_content)
    
    except Exception as e:
        current_app.logger.error(f"Failed to send credentials email: {str(e)}")
        return False

def send_result_notification_email(recipient_email: str, student_name: str, 
                                   subject: str, score: float, grade: str) -> bool:
    """
    Send result notification email to parent
    
    Args:
        recipient_email: Parent email
        student_name: Student name
        subject: Subject name
        score: Total score
        grade: Grade letter
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        email_subject = f"FVS Software - Result Notification for {student_name}"
        
        # Color code grades
        grade_color = '#00cc00' if grade in ['A', 'B'] else '#ff9900' if grade == 'C' else '#ff3333'
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <h2 style="color: #0099ff; text-align: center;">FVS Software</h2>
                    <hr style="border: none; border-top: 2px solid #00d4ff; margin: 20px 0;">
                    
                    <h3 style="color: #333;">Result Notification</h3>
                    
                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        Dear Parent/Guardian,<br><br>
                        A new result has been posted for your child.
                    </p>
                    
                    <div style="background-color: #f0f8ff; padding: 20px; border-left: 4px solid #00d4ff; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0 0 10px 0; color: #333;"><strong>Student:</strong> {student_name}</p>
                        <p style="margin: 0 0 10px 0; color: #333;"><strong>Subject:</strong> {subject}</p>
                        <p style="margin: 0 0 10px 0; color: #333;"><strong>Score:</strong> {score}/100</p>
                        <p style="margin: 0; color: #333;"><strong>Grade:</strong> <span style="font-size: 18px; color: {grade_color}; font-weight: bold;">{grade}</span></p>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">
                        To view the complete result details, please log in to your FVS Software parent account.
                    </p>
                    
                    <p style="color: #999; font-size: 12px; margin-top: 30px;">
                        Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        © 2026 Folusho Victory Schools. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return _send_email(recipient_email, email_subject, html_content)
    
    except Exception as e:
        current_app.logger.error(f"Failed to send result notification email: {str(e)}")
        return False

def _send_email(recipient_email: str, subject: str, html_content: str) -> bool:
    """
    Internal function to send email
    
    Args:
        recipient_email: Recipient email address
        subject: Email subject
        html_content: HTML content of email
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Validate email configuration
        if not SENDER_EMAIL or not SENDER_PASSWORD:
            current_app.logger.warning("Email configuration not set. Email not sent.")
            return False
        
        # Create email message
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = SENDER_EMAIL
        message['To'] = recipient_email
        
        # Attach HTML content
        part = MIMEText(html_content, 'html')
        message.attach(part)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        
        current_app.logger.info(f"Email sent successfully to {recipient_email}")
        return True
    
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        return False
