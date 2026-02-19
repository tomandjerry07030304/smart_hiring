#!/usr/bin/env python3
"""
Test Email Configuration
========================
Sends a test email using the credentials in .env to verify SMTP setup.
"""
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.utils.env_config import env_config
from backend.utils.email_service import email_service

# Configure logging to see details
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email():
    print("=" * 60)
    print("  TESTING EMAIL CONFIGURATION")
    print("=" * 60)
    
    # Check config
    print(f"  SMTP_ENABLED:  {os.getenv('SMTP_ENABLED')}")
    print(f"  SMTP_SERVER:   {os.getenv('SMTP_SERVER')}")
    print(f"  SMTP_PORT:     {os.getenv('SMTP_PORT')}")
    print(f"  SMTP_USERNAME: {os.getenv('SMTP_USERNAME')}")
    print(f"  FROM_EMAIL:    {os.getenv('SMTP_FROM_EMAIL')}")
    
    username = os.getenv('SMTP_USERNAME')
    if not username or "YOUR_BREVO_LOGIN_EMAIL_HERE" in username:
        print("\n❌ ERROR: SMTP_USERNAME is not set correctly in .env!")
        print("   Please replace 'YOUR_BREVO_LOGIN_EMAIL_HERE' with your actual Brevo login email.")
        return

    recipient = username  # Send to self for testing
    subject = "Smart Hiring System - Test Email 🚀"
    body = """
    <h1>Email System Verified! ✅</h1>
    <p>This is a test email from the Smart Hiring System.</p>
    <p>If you are reading this, your SMTP configuration with Brevo is working correctly.</p>
    <br>
    <p>Time: {}</p>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    print(f"\n  Attempting to send test email to: {recipient}...")
    
    try:
        success = email_service.send_email(
            to_email=recipient,
            subject=subject,
            html_content=body
        )
        
        if success:
            print("\n✅ SUCCESS: Email sent successfully!")
            print("   Check your inbox (and spam folder) for the test email.")
        else:
            print("\n❌ FAILED: Email service reported failure.")
            print("   Check the logs above for details.")
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email()
