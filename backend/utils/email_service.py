"""
Email Notification Service
Handles sending professional email notifications for various events

EXECUTION MODEL: SYNCHRONOUS
============================
This service sends emails SYNCHRONOUSLY (blocking).
- Pros: Simple, no Redis/Celery dependency, immediate feedback
- Cons: Slower API responses, not scalable for high volume

For ASYNCHRONOUS email sending:
- Use backend/tasks/email_tasks.py with Celery workers
- Requires Redis running and ENABLE_BACKGROUND_WORKERS=true
- Routes must call send_email_task.delay() instead of email_service methods

Updated: 2026-01-06 - Made behavior explicit and honest
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List

class EmailService:
    """Professional email service with template support"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@smarthiring.com')
        self.from_name = os.getenv('FROM_NAME', 'Smart Hiring System')
        # FIX: Default to TRUE - emails ENABLED by default in all non-test environments
        env = os.getenv('FLASK_ENV', 'production')
        self.enabled = os.getenv('EMAIL_ENABLED', 'true').lower() == 'true' and env != 'testing'
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Validate email configuration on startup and log status"""
        issues = []
        
        if not self.smtp_username:
            issues.append("SMTP_USERNAME not set")
        elif 'your-' in self.smtp_username or 'your@' in self.smtp_username:
            issues.append("SMTP_USERNAME contains placeholder value")
            
        if not self.smtp_password:
            issues.append("SMTP_PASSWORD not set")
        elif 'your-' in self.smtp_password:
            issues.append("SMTP_PASSWORD contains placeholder value")
            
        if issues:
            print(f"\n{'='*60}")
            print(f"⚠️  EMAIL CONFIGURATION WARNING")
            for issue in issues:
                print(f"   ❌ {issue}")
            print(f"\n💡 To fix: Set valid SMTP credentials in .env file")
            print(f"💡 For Gmail: https://myaccount.google.com/apppasswords")
            print(f"{'='*60}\n")
            self.config_valid = False
        else:
            print(f"✅ Email service configured: {self.smtp_server}:{self.smtp_port}")
            self.config_valid = True
        
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send an email with HTML and optional plain text content"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"📧 Email request: to={to_email}, subject={subject}")
        
        # FIX: Explicit check - if disabled, log and return False (not silent True)
        if not self.enabled:
            logger.warning(f"📧 EMAIL DISABLED by configuration - email NOT sent to {to_email}")
            print(f"⚠️  EMAIL DISABLED - Set EMAIL_ENABLED=true in .env")
            return False  # FIX: Return False - be honest about not sending
            
        # FIX: Validate credentials are real, not placeholders
        if not self.config_valid:
            logger.error(f"❌ EMAIL CONFIG INVALID - Cannot send to {to_email}")
            print(f"❌ SMTP credentials not configured properly - email NOT sent")
            return False  # FIX: Return False - be honest
            
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text version
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            # Add HTML version
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Send email
            print(f"🚀 Attempting to send email via SMTP...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.set_debuglevel(1)  # Enable SMTP debug output
                server.starttls()
                print(f"🔐 Logging in to SMTP server...")
                server.login(self.smtp_username, self.smtp_password)
                print(f"📤 Sending message...")
                server.send_message(msg)
                
            print(f"✅ EMAIL SENT SUCCESSFULLY to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ FAILED TO SEND EMAIL to {to_email}")
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_welcome_email(self, to_email: str, full_name: str, role: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to Smart Hiring System! 🎉"
        
        html_content = self._get_welcome_template(full_name, role)
        text_content = f"""
        Welcome to Smart Hiring System, {full_name}!
        
        Your account has been successfully created as a {role}.
        
        You can now log in and start using our platform.
        
        Best regards,
        Smart Hiring Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_application_confirmation(self, to_email: str, candidate_name: str, job_title: str, company_name: str) -> bool:
        """Send application confirmation to candidate"""
        subject = f"Application Received: {job_title}"
        
        html_content = self._get_application_confirmation_template(candidate_name, job_title, company_name)
        text_content = f"""
        Hi {candidate_name},
        
        Your application for {job_title} at {company_name} has been received.
        
        We will review your application and get back to you soon.
        
        Best of luck!
        Smart Hiring Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_status_update_email(self, to_email: str, candidate_name: str, job_title: str, 
                                 new_status: str, note: Optional[str] = None) -> bool:
        """Send status update notification to candidate"""
        status_messages = {
            'shortlisted': 'Congratulations! You have been shortlisted! 🎉',
            'interviewed': 'Interview Scheduled 📅',
            'hired': 'Congratulations! You are hired! 🎊',
            'rejected': 'Application Status Update'
        }
        
        subject = f"{status_messages.get(new_status, 'Application Status Update')}: {job_title}"
        
        html_content = self._get_status_update_template(candidate_name, job_title, new_status, note)
        text_content = f"""
        Hi {candidate_name},
        
        Your application for {job_title} has been updated to: {new_status.upper()}
        
        {f'Note: {note}' if note else ''}
        
        Best regards,
        Smart Hiring Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_email(self, to_email: str, reset_link: str, user_name: str) -> bool:
        """Send password reset email with secure link"""
        subject = "Password Reset Request - Smart Hiring System 🔐"
        
        html_content = self._get_password_reset_template(user_name, reset_link)
        text_content = f"""
        Hi {user_name},
        
        We received a request to reset your password for your Smart Hiring System account.
        
        Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 1 hour for security reasons.
        
        If you didn't request this password reset, please ignore this email.
        
        Best regards,
        Smart Hiring Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_new_application_alert(self, to_email: str, recruiter_name: str, candidate_name: str, 
                                   job_title: str, match_score: float) -> bool:
        """Send new application alert to recruiter"""
        subject = f"New Application: {candidate_name} for {job_title}"
        
        html_content = self._get_new_application_template(recruiter_name, candidate_name, job_title, match_score)
        text_content = f"""
        Hi {recruiter_name},
        
        You have received a new application from {candidate_name} for {job_title}.
        
        Match Score: {match_score}%
        
        Log in to review the application.
        
        Smart Hiring Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_job_posting_confirmation(self, to_email: str, company_name: str, job_title: str,
                                       job_id: str, location: str, job_type: str,
                                       description_summary: str = "") -> bool:
        """Send job posting confirmation email to company/recruiter"""
        subject = f"✅ Job Posted Successfully: {job_title}"
        
        html_content = self._get_job_posting_template(
            company_name, job_title, job_id, location, job_type, description_summary
        )
        text_content = f"""
        Hi {company_name},
        
        Your job posting has been successfully created!
        
        Job Details:
        - Title: {job_title}
        - Job ID: {job_id}
        - Location: {location or 'Not specified'}
        - Type: {job_type or 'Full-time'}
        - Status: Active
        - Posted: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        
        Your job is now live and visible to candidates.
        
        You can manage your posting anytime from your dashboard.
        
        Best regards,
        Smart Hiring Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_login_confirmation(self, to_email: str, user_name: str, login_time: str = None,
                                 ip_address: str = None, device_info: str = None) -> bool:
        """Send login confirmation/security alert email to user"""
        from datetime import datetime
        
        if not login_time:
            login_time = datetime.now().strftime('%B %d, %Y at %I:%M %p UTC')
        
        subject = "🔐 New Login to Your Smart Hiring Account"
        
        html_content = self._get_login_confirmation_template(
            user_name, login_time, ip_address, device_info
        )
        text_content = f"""
        Hi {user_name},
        
        We detected a new login to your Smart Hiring account.
        
        Login Details:
        - Time: {login_time}
        - IP Address: {ip_address or 'Unknown'}
        - Device: {device_info or 'Unknown'}
        
        If this was you, no action is needed.
        
        If you didn't log in, please:
        1. Change your password immediately
        2. Contact our support team
        
        Stay secure!
        Smart Hiring Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def _get_base_template(self, content: str) -> str:
        """Base HTML email template with professional styling"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background-color: #f7fafc;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #4F46E5 0%, #7c3aed 100%);
                    padding: 40px 32px;
                    text-align: center;
                }}
                .logo {{
                    color: white;
                    font-size: 32px;
                    font-weight: 700;
                    margin-bottom: 8px;
                }}
                .tagline {{
                    color: rgba(255,255,255,0.9);
                    font-size: 14px;
                }}
                .content {{
                    padding: 40px 32px;
                    color: #1a202c;
                    line-height: 1.6;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 32px;
                    background: linear-gradient(135deg, #4F46E5 0%, #7c3aed 100%);
                    color: white !important;
                    text-decoration: none;
                    border-radius: 12px;
                    font-weight: 600;
                    margin: 24px 0;
                }}
                .footer {{
                    padding: 32px;
                    text-align: center;
                    background: #f7fafc;
                    color: #718096;
                    font-size: 14px;
                }}
                .status-badge {{
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-weight: 600;
                    margin: 16px 0;
                }}
                .status-shortlisted {{ background: #fef3c7; color: #78350f; }}
                .status-interviewed {{ background: #f3e8ff; color: #581c87; }}
                .status-hired {{ background: #d1fae5; color: #065f46; }}
                .status-rejected {{ background: #fee2e2; color: #991b1b; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎯 Smart Hiring</div>
                    <div class="tagline">Your Gateway to Better Talent Management</div>
                </div>
                <div class="content">
                    {content}
                </div>
                <div class="footer">
                    <p>© {datetime.now().year} Smart Hiring System. All rights reserved.</p>
                    <p>You received this email because you have an account with us.</p>
                    <p><a href="https://my-project-smart-hiring.onrender.com" style="color: #4F46E5;">Visit Dashboard</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_welcome_template(self, full_name: str, role: str) -> str:
        """Welcome email template"""
        content = f"""
            <h2>Welcome aboard, {full_name}! 🎉</h2>
            <p>Your account has been successfully created as a <strong>{role}</strong>.</p>
            <p>You can now access all the features available for your role:</p>
            <ul>
                {'<li>Browse and apply to job postings</li><li>Track your application status</li><li>Complete skill assessments</li><li>Build your professional profile</li>' if role == 'candidate' else ''}
                {'<li>Post new job openings</li><li>Review applications</li><li>Manage candidates</li><li>Track hiring metrics</li>' if role == 'company' else ''}
                {'<li>Full system administration</li><li>User management</li><li>System analytics</li>' if role == 'admin' else ''}
            </ul>
            <p>
                <a href="https://my-project-smart-hiring.onrender.com" class="button">
                    Get Started →
                </a>
            </p>
            <p>If you have any questions, feel free to reach out to our support team.</p>
            <p>Best regards,<br><strong>Smart Hiring Team</strong></p>
        """
        return self._get_base_template(content)
    
    def _get_application_confirmation_template(self, candidate_name: str, job_title: str, company_name: str) -> str:
        """Application confirmation template"""
        content = f"""
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
            <p>
                <a href="https://my-project-smart-hiring.onrender.com" class="button">
                    View Application Status →
                </a>
            </p>
            <p>Good luck! 🍀</p>
            <p>Best regards,<br><strong>Smart Hiring Team</strong></p>
        """
        return self._get_base_template(content)
    
    def _get_status_update_template(self, candidate_name: str, job_title: str, new_status: str, note: Optional[str]) -> str:
        """Status update email template"""
        status_messages = {
            'shortlisted': ('🎉 Congratulations!', 'You have been shortlisted for the next round.'),
            'interviewed': ('📅 Interview Scheduled', 'Your interview has been scheduled.'),
            'hired': ('🎊 You\'re Hired!', 'Congratulations on your new position!'),
            'rejected': ('Application Update', 'Thank you for your interest.')
        }
        
        title, message = status_messages.get(new_status, ('Status Update', 'Your application status has been updated.'))
        
        content = f"""
            <h2>{title}</h2>
            <p>Hi <strong>{candidate_name}</strong>,</p>
            <p>{message}</p>
            <p>Your application for <strong>{job_title}</strong> has been updated to:</p>
            <div class="status-badge status-{new_status}">
                {new_status.upper()}
            </div>
            {f'<p><strong>Note from recruiter:</strong><br>{note}</p>' if note else ''}
            <p>
                <a href="https://my-project-smart-hiring.onrender.com" class="button">
                    View Details →
                </a>
            </p>
            <p>Best regards,<br><strong>Smart Hiring Team</strong></p>
        """
        return self._get_base_template(content)
    
    def _get_password_reset_template(self, user_name: str, reset_link: str) -> str:
        """Password reset email template"""
        content = f"""
            <h2>Password Reset Request 🔐</h2>
            <p>Hi <strong>{user_name}</strong>,</p>
            <p>We received a request to reset your password for your Smart Hiring System account.</p>
            <p>Click the button below to create a new password:</p>
            <p>
                <a href="{reset_link}" class="button">
                    Reset Password →
                </a>
            </p>
            <p><strong>Important:</strong></p>
            <ul>
                <li>This link will expire in <strong>1 hour</strong> for security reasons</li>
                <li>If you didn't request this reset, please ignore this email</li>
                <li>Your password will remain unchanged unless you click the link</li>
            </ul>
            <p>For security reasons, if you continue to experience issues, please contact our support team.</p>
            <p>Best regards,<br><strong>Smart Hiring Team</strong></p>
        """
        return self._get_base_template(content)
    
    def _get_new_application_template(self, recruiter_name: str, candidate_name: str, job_title: str, match_score: float) -> str:
        """New application alert for recruiter"""
        score_color = '#065f46' if match_score >= 80 else '#7c2d12' if match_score >= 60 else '#991b1b'
        
        content = f"""
            <h2>New Application Received! 📋</h2>
            <p>Hi <strong>{recruiter_name}</strong>,</p>
            <p>You have received a new application from <strong>{candidate_name}</strong> for the position:</p>
            <h3 style="color: #4F46E5;">{job_title}</h3>
            <div style="background: #f7fafc; padding: 20px; border-radius: 12px; margin: 24px 0;">
                <p style="margin: 0; color: #718096;">Match Score</p>
                <h2 style="margin: 8px 0; color: {score_color};">{int(match_score)}%</h2>
            </div>
            <p>
                <a href="https://my-project-smart-hiring.onrender.com" class="button">
                    Review Application →
                </a>
            </p>
            <p>Best regards,<br><strong>Smart Hiring System</strong></p>
        """
        return self._get_base_template(content)
    
    def _get_job_posting_template(self, company_name: str, job_title: str, job_id: str,
                                   location: str, job_type: str, description_summary: str) -> str:
        """Job posting confirmation template for recruiter/company"""
        content = f"""
            <h2>Job Posted Successfully! 🎉</h2>
            <p>Hi <strong>{company_name}</strong>,</p>
            <p>Your job posting has been created and is now <strong style="color: #065f46;">LIVE</strong>!</p>
            
            <div style="background: #f7fafc; padding: 24px; border-radius: 12px; margin: 24px 0; border-left: 4px solid #4F46E5;">
                <h3 style="margin: 0 0 16px 0; color: #4F46E5;">{job_title}</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #718096; width: 120px;">Job ID:</td>
                        <td style="padding: 8px 0; font-weight: 600;">{job_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #718096;">Location:</td>
                        <td style="padding: 8px 0;">{location or 'Remote / Not specified'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #718096;">Job Type:</td>
                        <td style="padding: 8px 0;">{job_type}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #718096;">Status:</td>
                        <td style="padding: 8px 0;"><span style="background: #d1fae5; color: #065f46; padding: 4px 12px; border-radius: 4px; font-weight: 600;">Active</span></td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #718096;">Posted:</td>
                        <td style="padding: 8px 0;">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</td>
                    </tr>
                </table>
                {f'<p style="margin-top: 16px; color: #4a5568;"><strong>Description:</strong><br>{description_summary}</p>' if description_summary else ''}
            </div>
            
            <p><strong>What's Next?</strong></p>
            <ul>
                <li>Your job is now visible to all candidates</li>
                <li>You'll receive email alerts for new applications</li>
                <li>Review and manage applications from your dashboard</li>
            </ul>
            
            <p>
                <a href="https://my-project-smart-hiring.onrender.com" class="button">
                    View Job Posting →
                </a>
            </p>
            <p>Best regards,<br><strong>Smart Hiring Team</strong></p>
        """
        return self._get_base_template(content)
    
    def _get_login_confirmation_template(self, user_name: str, login_time: str,
                                          ip_address: str = None, device_info: str = None) -> str:
        """Login confirmation/security alert template"""
        content = f"""
            <h2>New Login Detected 🔐</h2>
            <p>Hi <strong>{user_name}</strong>,</p>
            <p>We noticed a new login to your Smart Hiring account.</p>
            
            <div style="background: #f0fdf4; padding: 24px; border-radius: 12px; margin: 24px 0; border-left: 4px solid #22c55e;">
                <h3 style="margin: 0 0 16px 0; color: #166534;">Login Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #718096; width: 120px;">Time:</td>
                        <td style="padding: 8px 0; font-weight: 600;">{login_time}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #718096;">IP Address:</td>
                        <td style="padding: 8px 0;">{ip_address or 'Not available'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #718096;">Device:</td>
                        <td style="padding: 8px 0;">{device_info or 'Not available'}</td>
                    </tr>
                </table>
            </div>
            
            <p><strong>Was this you?</strong></p>
            <p style="color: #065f46;">✅ If yes, you can safely ignore this email.</p>
            
            <div style="background: #fef2f2; padding: 16px; border-radius: 8px; margin: 16px 0;">
                <p style="margin: 0; color: #991b1b;">
                    <strong>⚠️ If this wasn't you:</strong><br>
                    Someone may have access to your account. Please take these steps immediately:
                </p>
                <ol style="color: #991b1b; margin: 8px 0;">
                    <li>Change your password right away</li>
                    <li>Review your recent account activity</li>
                    <li>Contact our support team</li>
                </ol>
            </div>
            
            <p>
                <a href="https://my-project-smart-hiring.onrender.com" class="button">
                    Go to Dashboard →
                </a>
            </p>
            <p>Stay secure!<br><strong>Smart Hiring Team</strong></p>
        """
        return self._get_base_template(content)

# Global email service instance
email_service = EmailService()
