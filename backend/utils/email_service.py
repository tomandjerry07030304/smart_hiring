"""
Email Notification Service
Handles sending professional email notifications for various events
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
        self.enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
        
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send an email with HTML and optional plain text content"""
        if not self.enabled:
            print(f"📧 Email disabled. Would send to {to_email}: {subject}")
            return True
            
        if not self.smtp_username or not self.smtp_password:
            print(f"⚠️ SMTP credentials not configured. Skipping email to {to_email}")
            return False
            
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
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
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

# Global email service instance
email_service = EmailService()
