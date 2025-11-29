# Email Notification System Configuration

## Overview
The Smart Hiring System now includes a professional email notification service that sends emails for:
- Welcome emails (new user registration)
- Application confirmations (candidate applies to job)
- Status updates (recruiter changes application status)
- New application alerts (recruiter receives new application)

## Email Service Configuration

### Required Environment Variables

Add these to your `.env` file (local) or Render environment variables (production):

```bash
# Email Service Configuration
EMAIL_ENABLED=true                          # Set to 'true' to enable email sending
SMTP_SERVER=smtp.gmail.com                  # Your SMTP server
SMTP_PORT=587                               # SMTP port (usually 587 for TLS)
SMTP_USERNAME=your-email@gmail.com          # Your email address
SMTP_PASSWORD=your-app-password             # Your email password or app password
FROM_EMAIL=noreply@smarthiring.com          # From email address
FROM_NAME=Smart Hiring System               # From name displayed in emails
```

### Setting Up Gmail (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Google account

2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password
   - Use this as `SMTP_PASSWORD` (remove spaces)

3. **Configuration:**
   ```bash
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=yourname@gmail.com
   SMTP_PASSWORD=abcd efgh ijkl mnop  # (remove spaces)
   FROM_EMAIL=yourname@gmail.com
   FROM_NAME=Smart Hiring System
   EMAIL_ENABLED=true
   ```

### Alternative SMTP Providers

#### SendGrid (Production Recommended)
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Smart Hiring System
EMAIL_ENABLED=true
```

#### Mailgun
```bash
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Smart Hiring System
EMAIL_ENABLED=true
```

#### AWS SES
```bash
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-aws-smtp-username
SMTP_PASSWORD=your-aws-smtp-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Smart Hiring System
EMAIL_ENABLED=true
```

## Email Templates

The system includes professional HTML email templates with:
- Responsive design
- Company branding (purple gradient theme)
- Clear call-to-action buttons
- Footer with unsubscribe options

### Available Templates

1. **Welcome Email** - Sent when user registers
2. **Application Confirmation** - Sent when candidate applies
3. **Status Update** - Sent when application status changes
4. **New Application Alert** - Sent to recruiter on new application

## Email Preferences

Users can manage their email preferences at:
`/email-preferences.html`

### Preference Categories

**Transactional (Always Enabled):**
- Welcome emails
- Application confirmations
- Status updates

**Marketing (User Controlled):**
- New job alerts
- Newsletter
- Marketing communications

## API Endpoints

### Get Email Preferences
```http
GET /api/email/preferences
Authorization: Bearer {token}

Response:
{
  "preferences": {
    "welcome_emails": true,
    "application_confirmations": true,
    "status_updates": true,
    "new_job_alerts": true,
    "newsletter": true,
    "marketing": false
  },
  "email": "user@example.com"
}
```

### Update Email Preferences
```http
PUT /api/email/preferences
Authorization: Bearer {token}
Content-Type: application/json

{
  "new_job_alerts": false,
  "newsletter": false,
  "marketing": false
}

Response:
{
  "message": "Email preferences updated successfully",
  "preferences": { ... }
}
```

### Unsubscribe (No Auth Required)
```http
POST /api/email/unsubscribe
Content-Type: application/json

{
  "email": "user@example.com",
  "token": "unsubscribe-token"
}

Response:
{
  "message": "Successfully unsubscribed from marketing emails",
  "note": "You will still receive important transactional emails"
}
```

## Testing Email System

### Local Testing (Without SMTP)
Set `EMAIL_ENABLED=false` in your `.env` file. The system will:
- Log email attempts to console
- Continue normal operation
- Show "Would send email to..." messages

### Production Testing
1. Set up real SMTP credentials
2. Set `EMAIL_ENABLED=true`
3. Register a test user
4. Check email inbox for welcome message

## Troubleshooting

### Emails Not Sending

**Check 1: Environment Variables**
```bash
# Verify variables are set on Render
echo $EMAIL_ENABLED
echo $SMTP_SERVER
echo $SMTP_USERNAME
```

**Check 2: SMTP Authentication**
- Gmail: Ensure App Password is generated correctly
- Other: Verify API keys and credentials

**Check 3: Firewall/Port**
- Port 587 should be open for TLS
- Port 465 for SSL (if used)

**Check 4: Logs**
```bash
# Check application logs on Render
# Look for: ✅ Email sent successfully
# Or: ❌ Failed to send email
```

### Common Errors

**"SMTP AUTH extension not supported by server"**
- Check SMTP_SERVER is correct
- Verify port (587 for TLS)

**"Username and Password not accepted"**
- Gmail: Generate new App Password
- Other: Verify credentials

**"SMTPServerDisconnected"**
- Server may be down
- Check network connectivity
- Try alternative SMTP provider

## Best Practices

### For Development
- Use Gmail with App Password
- Keep `EMAIL_ENABLED=false` for rapid testing
- Check console logs for email content

### For Production
- Use dedicated service (SendGrid/Mailgun)
- Set up custom domain for FROM_EMAIL
- Enable email logging/monitoring
- Implement rate limiting
- Add email delivery tracking

### Security
- Never commit SMTP credentials to Git
- Use environment variables
- Rotate passwords regularly
- Monitor for unauthorized access
- Implement SPF/DKIM/DMARC records

## Deployment on Render

1. Go to Render Dashboard
2. Select your service
3. Navigate to "Environment" tab
4. Add all required variables:
   ```
   EMAIL_ENABLED = true
   SMTP_SERVER = smtp.gmail.com
   SMTP_PORT = 587
   SMTP_USERNAME = your-email@gmail.com
   SMTP_PASSWORD = your-app-password
   FROM_EMAIL = noreply@smarthiring.com
   FROM_NAME = Smart Hiring System
   ```
5. Click "Save Changes"
6. Render will auto-deploy with new configuration

## Monitoring

### Success Metrics
- Email delivery rate
- Open rates
- Click-through rates
- Bounce rates
- Unsubscribe rates

### Logging
All email operations are logged:
```
✅ Email sent successfully to user@example.com
❌ Failed to send email to user@example.com: [error]
📧 Email disabled. Would send to user@example.com: [subject]
⚠️ SMTP credentials not configured. Skipping email
```

## Support

For email system issues:
- Check logs first
- Verify environment variables
- Test SMTP credentials manually
- Contact support: admin@smarthiring.com

---

**Version:** 1.0.0  
**Last Updated:** January 2025  
**Status:** ✅ Production Ready
