"""
Email sending tasks
"""

from backend.celery_config import celery_app, SafeTask
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


@celery_app.task(base=SafeTask, bind=True, name='send_email')
def send_email_task(self, to_email, subject, body, html_body=None):
    """
    Send email asynchronously
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Plain text body
        html_body: Optional HTML body
    """
    try:
        # SMTP configuration
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        from_email = os.getenv('FROM_EMAIL', smtp_username)
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Add plain text part
        msg.attach(MIMEText(body, 'plain'))
        
        # Add HTML part if provided
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return {'status': 'sent', 'to': to_email, 'timestamp': datetime.utcnow().isoformat()}
        
    except Exception as e:
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)


@celery_app.task(base=SafeTask, name='send_welcome_email')
def send_welcome_email(user_email, user_name):
    """Send welcome email to new users"""
    subject = "Welcome to Smart Hiring System!"
    body = f"""
    Hi {user_name},
    
    Welcome to Smart Hiring System! Your account has been successfully created.
    
    You can now:
    - Browse job postings
    - Apply to positions
    - Take skill assessments
    - Track your applications
    
    Best regards,
    Smart Hiring Team
    """
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Welcome to Smart Hiring System!</h2>
            <p>Hi {user_name},</p>
            <p>Welcome to Smart Hiring System! Your account has been successfully created.</p>
            <h3>You can now:</h3>
            <ul>
                <li>Browse job postings</li>
                <li>Apply to positions</li>
                <li>Take skill assessments</li>
                <li>Track your applications</li>
            </ul>
            <p>Best regards,<br>Smart Hiring Team</p>
        </body>
    </html>
    """
    
    return send_email_task.delay(user_email, subject, body, html_body)


@celery_app.task(base=SafeTask, name='send_verification_email')
def send_verification_email(user_email, user_name, verification_token):
    """
    Send email verification link to new user
    Priority: Critical
    """
    base_url = os.getenv('FRONTEND_URL', 'http://localhost:5000')
    verification_link = f"{base_url}/api/auth/verify-email?token={verification_token}&email={user_email}"
    
    subject = "🔐 Verify Your Email - Smart Hiring System"
    
    body = f"""
    Hi {user_name},
    
    Please verify your email address to complete your registration.
    
    Click the link below to verify:
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't create an account, please ignore this email.
    
    Best regards,
    Smart Hiring Team
    """
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Verify Your Email Address 🔐</h2>
            <p>Hi <strong>{user_name}</strong>,</p>
            <p>Thank you for registering with Smart Hiring System!</p>
            <p>Please click the button below to verify your email address:</p>
            <p>
                <a href="{verification_link}" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Verify My Email
                </a>
            </p>
            <p><strong>Important:</strong></p>
            <ul>
                <li>This link will expire in <strong>24 hours</strong></li>
                <li>If you didn't create this account, please ignore this email</li>
            </ul>
            <p style="font-size: 12px; color: #718096; margin-top: 24px;">
                If the button doesn't work, copy and paste this link:<br>
                <a href="{verification_link}">{verification_link}</a>
            </p>
            <p>Best regards,<br><strong>Smart Hiring Team</strong></p>
        </body>
    </html>
    """
    
    return send_email_task.delay(user_email, subject, body, html_body)


@celery_app.task(base=SafeTask, name='send_new_application_alert')
def send_new_application_alert(recruiter_email, recruiter_name, candidate_name, job_title, match_score):
    """
    Send new application alert to recruiter
    Priority: High
    """
    subject = f"New Application: {candidate_name} for {job_title}"
    
    # Determine score color
    score_color = '#065f46' if match_score >= 80 else '#7c2d12' if match_score >= 60 else '#991b1b'
    
    body = f"""
    Hi {recruiter_name},
    
    You have received a new application from {candidate_name} for {job_title}.
    
    Match Score: {int(match_score)}%
    
    Log in to review the application.
    
    Smart Hiring Team
    """
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>New Application Received! 📋</h2>
            <p>Hi <strong>{recruiter_name}</strong>,</p>
            <p>You have received a new application from <strong>{candidate_name}</strong> for the position:</p>
            <h3 style="color: #4F46E5;">{job_title}</h3>
            <div style="background: #f7fafc; padding: 20px; border-radius: 12px; margin: 24px 0;">
                <p style="margin: 0; color: #718096;">Match Score</p>
                <h2 style="margin: 8px 0; color: {score_color};">{int(match_score)}%</h2>
            </div>
            <p>
                <a href="https://my-project-smart-hiring.onrender.com" style="background-color: #4F46E5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Review Application
                </a>
            </p>
            <p>Best regards,<br><strong>Smart Hiring System</strong></p>
        </body>
    </html>
    """
    
    return send_email_task.delay(recruiter_email, subject, body, html_body)


@celery_app.task(base=SafeTask, name='send_application_confirmation')
def send_application_confirmation(candidate_email, candidate_name, job_title, company_name):
    """
    Send application confirmation to candidate
    Priority: Medium
    """
    subject = f"Application Received: {job_title}"
    
    body = f"""
    Hi {candidate_name},
    
    Your application for {job_title} at {company_name} has been received.
    
    We will review your application and get back to you soon.
    
    Best of luck!
    Smart Hiring Team
    """
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Application Received! ✅</h2>
            <p>Hi <strong>{candidate_name}</strong>,</p>
            <p>Your application for <strong>{job_title}</strong> at <strong>{company_name}</strong> has been successfully submitted.</p>
            <p><strong>What happens next?</strong></p>
            <ol>
                <li>Our team will review your application</li>
                <li>We'll match your skills with job requirements</li>
                <li>You'll be notified about any status updates</li>
            </ol>
            <p>You can track your application status anytime in your dashboard.</p>
            <p>Good luck! 🍀</p>
            <p>Best regards,<br><strong>Smart Hiring Team</strong></p>
        </body>
    </html>
    """
    
    return send_email_task.delay(candidate_email, subject, body, html_body)


@celery_app.task(base=SafeTask, name='send_application_status_email')
def send_application_status_email(user_email, job_title, new_status):
    """Send email when application status changes"""
    subject = f"Application Update: {job_title}"
    body = f"""
    Your application for {job_title} has been updated.
    
    New Status: {new_status}
    
    You can view more details in your dashboard.
    
    Best regards,
    Smart Hiring Team
    """
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Application Update</h2>
            <p>Your application for <strong>{job_title}</strong> has been updated.</p>
            <p><strong>New Status:</strong> {new_status}</p>
            <p>You can view more details in your dashboard.</p>
            <p>Best regards,<br>Smart Hiring Team</p>
        </body>
    </html>
    """
    
    return send_email_task.delay(user_email, subject, body, html_body)


@celery_app.task(base=SafeTask, name='send_quiz_invitation')
def send_quiz_invitation(user_email, user_name, quiz_title, quiz_link):
    """Send quiz invitation email"""
    subject = f"Assessment Invitation: {quiz_title}"
    body = f"""
    Hi {user_name},
    
    You have been invited to take an assessment: {quiz_title}
    
    Please click the link below to begin:
    {quiz_link}
    
    Best regards,
    Smart Hiring Team
    """
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Assessment Invitation</h2>
            <p>Hi {user_name},</p>
            <p>You have been invited to take an assessment: <strong>{quiz_title}</strong></p>
            <p><a href="{quiz_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Start Assessment</a></p>
            <p>Best regards,<br>Smart Hiring Team</p>
        </body>
    </html>
    """
    
    return send_email_task.delay(user_email, subject, body, html_body)


@celery_app.task(base=SafeTask, name='send_daily_digest')
def send_daily_digest(hour=9):
    """
    Send daily digest to users with new job matches
    (Scheduled task - runs daily)
    """
    from backend.db import get_db
    
    db = get_db()
    users = db.users.find({'email_preferences.new_job_alerts': True})
    
    for user in users:
        # Find matching jobs (simplified)
        matching_jobs = db.jobs.find({'status': 'open'}).limit(5)
        
        if matching_jobs:
            subject = "Your Daily Job Matches"
            body = f"Hi {user['name']},\n\nHere are today's job matches..."
            
            send_email_task.delay(user['email'], subject, body)
    
    return {'status': 'completed', 'users_notified': users.count()}


# Export
__all__ = [
    'send_email_task',
    'send_welcome_email',
    'send_application_status_email',
    'send_quiz_invitation',
    'send_daily_digest'
]