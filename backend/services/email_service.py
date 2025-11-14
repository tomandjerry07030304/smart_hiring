"""
Email Notification System
Send emails for application confirmations, interview schedules, status updates
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

class EmailNotificationSystem:
    """Handle all email notifications"""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = self.smtp_user or 'noreply@smarthiring.com'
        
    def send_email(self, to_email, subject, html_content):
        """Send HTML email"""
        if not self.smtp_user or not self.smtp_password:
            print(f"📧 [DEMO MODE] Email to {to_email}: {subject}")
            print(f"   Content preview: {html_content[:100]}...")
            return True
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False
    
    def send_application_confirmation(self, candidate_email, candidate_name, job_title, company):
        """Send application confirmation email"""
        subject = f"Application Received - {job_title}"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                <h1>🚀 Application Received!</h1>
            </div>
            <div style="padding: 30px;">
                <p>Hi {candidate_name},</p>
                <p>Thank you for applying to the <strong>{job_title}</strong> position at <strong>{company}</strong>.</p>
                <p>Your application is being reviewed by our AI-powered system. We'll notify you of the next steps soon.</p>
                
                <div style="background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3>What happens next?</h3>
                    <ul>
                        <li>🔍 Automated resume screening (bias-free)</li>
                        <li>📊 Skill matching analysis</li>
                        <li>⚖️ Fairness audit</li>
                        <li>👥 Recruiter review</li>
                    </ul>
                </div>
                
                <p>Best regards,<br>Smart Hiring Team</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(candidate_email, subject, html)
    
    def send_interview_invitation(self, candidate_email, candidate_name, job_title, interview_date, meeting_link):
        """Send interview invitation"""
        subject = f"Interview Invitation - {job_title}"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                <h1>🎉 Interview Invitation!</h1>
            </div>
            <div style="padding: 30px;">
                <p>Congratulations {candidate_name}!</p>
                <p>We're pleased to invite you for an interview for the <strong>{job_title}</strong> position.</p>
                
                <div style="background: #e0e7ff; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #667eea;">
                    <h3>Interview Details</h3>
                    <p><strong>Date & Time:</strong> {interview_date}</p>
                    <p><strong>Meeting Link:</strong> <a href="{meeting_link}">{meeting_link}</a></p>
                </div>
                
                <p>Please confirm your attendance by replying to this email.</p>
                <p>Good luck!</p>
                <p>Best regards,<br>Smart Hiring Team</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(candidate_email, subject, html)
    
    def send_status_update(self, candidate_email, candidate_name, job_title, status, message):
        """Send application status update"""
        status_emoji = {
            'accepted': '✅',
            'rejected': '❌',
            'pending': '⏳',
            'interview': '📅'
        }
        
        subject = f"Application Update - {job_title}"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                <h1>{status_emoji.get(status, '📧')} Application Update</h1>
            </div>
            <div style="padding: 30px;">
                <p>Hi {candidate_name},</p>
                <p>We have an update regarding your application for <strong>{job_title}</strong>.</p>
                
                <div style="background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <p><strong>Status:</strong> {status.upper()}</p>
                    <p>{message}</p>
                </div>
                
                <p>Best regards,<br>Smart Hiring Team</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(candidate_email, subject, html)

# Demo usage
if __name__ == '__main__':
    print("\n" + "="*60)
    print("📧 EMAIL NOTIFICATION SYSTEM - DEMO")
    print("="*60)
    
    email_system = EmailNotificationSystem()
    
    # Send demo emails
    email_system.send_application_confirmation(
        'jane.smith@email.com',
        'Jane Smith',
        'Senior Python Developer',
        'Tech Corp'
    )
    
    email_system.send_interview_invitation(
        'jane.smith@email.com',
        'Jane Smith',
        'Senior Python Developer',
        'November 20, 2025 at 2:00 PM',
        'https://meet.google.com/abc-defg-hij'
    )
    
    email_system.send_status_update(
        'aarav.sharma@email.com',
        'Aarav Sharma',
        'Senior Python Developer',
        'pending',
        'Your application is currently under review. We will contact you within 5 business days.'
    )
    
    print("\n✅ Email system ready (running in demo mode - set SMTP credentials in .env to send real emails)")
    print("="*60 + "\n")
