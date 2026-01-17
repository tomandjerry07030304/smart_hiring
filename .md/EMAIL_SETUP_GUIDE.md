# 📧 Universal Email Setup Guide
## Automated Email System for Smart Hiring System

This guide shows how to configure automated emails with **ANY email provider** (Gmail, Yahoo, Outlook, Custom SMTP, etc.)

---

## 🎯 **What Emails Are Automated?**

### ✅ **Already Integrated & Working:**

1. **Welcome Email** - Sent automatically when user registers
2. **Password Reset Email** - Sent automatically when user requests reset
3. **Application Confirmation** - Sent when candidate applies to job
4. **Status Update Email** - Sent when application status changes
5. **New Application Alert** - Sent to recruiter when they receive application

**Total:** 5 automated email types ready to use!

---

## 🔧 **Quick Setup (Choose Your Provider)**

### Option 1: Gmail (Most Common) ⭐

```bash
# 1. Enable 2-Step Verification in your Google Account
# 2. Generate App Password: https://myaccount.google.com/apppasswords
# 3. Add to your .env file:

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=Smart Hiring System
EMAIL_ENABLED=true
```

**Gmail App Password Steps:**
1. Go to Google Account → Security
2. Enable "2-Step Verification"
3. Go to "App passwords"
4. Select "Mail" and "Other (Custom name)"
5. Copy the 16-character password
6. Use this password in `SMTP_PASSWORD`

---

### Option 2: Yahoo Mail

```bash
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@yahoo.com
FROM_NAME=Smart Hiring System
EMAIL_ENABLED=true
```

**Yahoo App Password Steps:**
1. Go to Yahoo Account Security
2. Enable "Two-step verification"
3. Generate App Password
4. Use generated password in config

---

### Option 3: Outlook/Hotmail

```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
FROM_EMAIL=your-email@outlook.com
FROM_NAME=Smart Hiring System
EMAIL_ENABLED=true
```

---

### Option 4: Custom Domain (cPanel/WHM)

```bash
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=your-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Smart Hiring System
EMAIL_ENABLED=true
```

---

### Option 5: Professional Services

#### **SendGrid** (Recommended for Production)
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=verified-sender@yourdomain.com
FROM_NAME=Smart Hiring System
EMAIL_ENABLED=true
```

#### **AWS SES** (Amazon)
```bash
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
FROM_EMAIL=verified@yourdomain.com
FROM_NAME=Smart Hiring System
EMAIL_ENABLED=true
```

#### **Mailgun**
```bash
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@yourdomain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Smart Hiring System
EMAIL_ENABLED=true
```

---

## 🚀 **Setup on Render.com (Production)**

1. Go to your Render.com dashboard
2. Select your web service
3. Go to "Environment" tab
4. Add these environment variables:
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   FROM_EMAIL=your-email@gmail.com
   FROM_NAME=Smart Hiring System
   EMAIL_ENABLED=true
   FRONTEND_URL=https://my-project-smart-hiring.onrender.com
   ```
5. Click "Save Changes"
6. Your app will automatically redeploy with email enabled

---

## ✅ **Testing Your Email Setup**

### Method 1: Registration Test
1. Go to your deployed app
2. Register a new user
3. Check your email for welcome message
4. ✅ If you receive it, emails are working!

### Method 2: Password Reset Test
1. Go to login page
2. Click "Forgot Password"
3. Enter your email
4. Check inbox for reset link
5. ✅ Emails are configured correctly!

### Method 3: Local Testing
```bash
# Add to .env file
EMAIL_ENABLED=true
DEBUG=true

# Start the app
python app.py

# The console will show email logs
```

---

## 🔒 **Security Best Practices**

### ✅ **DO:**
- Use App Passwords (never your actual password)
- Enable 2FA on email account
- Use environment variables (never commit passwords)
- Use professional email service for production (SendGrid, SES)
- Verify sender domain (SPF, DKIM, DMARC)

### ❌ **DON'T:**
- Commit SMTP credentials to Git
- Use personal email password directly
- Disable 2FA after generating app password
- Send emails from unverified domains
- Expose SMTP credentials in logs

---

## 📊 **Email Templates Included**

### 1. Welcome Email
**Trigger:** User registration  
**Sent to:** New user  
**Content:** Welcome message, role info, get started button

### 2. Password Reset Email
**Trigger:** Forgot password request  
**Sent to:** User requesting reset  
**Content:** Secure reset link (1-hour expiry)

### 3. Application Confirmation
**Trigger:** Candidate applies to job  
**Sent to:** Candidate  
**Content:** Application received, next steps

### 4. Status Update Email
**Trigger:** Recruiter updates application status  
**Sent to:** Candidate  
**Content:** New status, recruiter notes

### 5. New Application Alert
**Trigger:** New application submitted  
**Sent to:** Recruiter  
**Content:** Candidate name, job title, match score

---

## 🎨 **Email Features**

✅ Professional HTML templates with gradients  
✅ Mobile-responsive design  
✅ Branded header with logo  
✅ Call-to-action buttons  
✅ Footer with unsubscribe info  
✅ Plain text fallback  
✅ Non-blocking (won't slow down API)  
✅ Error handling (app continues if email fails)

---

## 🔧 **Troubleshooting**

### Issue: "Authentication failed"
**Solution:** 
- Gmail: Generate new App Password
- Yahoo: Enable "Allow apps that use less secure sign in"
- Outlook: Check password is correct

### Issue: "Connection timeout"
**Solution:**
- Check SMTP_SERVER and SMTP_PORT
- Try port 465 (SSL) instead of 587 (TLS)
- Check firewall settings

### Issue: "Emails not sending"
**Solution:**
- Set `EMAIL_ENABLED=true`
- Check logs for error messages
- Verify SMTP credentials
- Test with simple email client first

### Issue: "Emails go to spam"
**Solution:**
- Verify sender domain (add SPF records)
- Use professional email service
- Don't use keywords like "free", "urgent"
- Add unsubscribe link

---

## 📈 **Recommended for Production**

### Free Tier Options:
1. **SendGrid** - 100 emails/day free
2. **Mailgun** - 5,000 emails/month free (3 months)
3. **AWS SES** - 62,000 emails/month free (if using EC2)

### Paid Options:
1. **SendGrid** - $14.95/month for 50k emails
2. **Mailgun** - $35/month for 50k emails
3. **AWS SES** - $0.10 per 1,000 emails

### Why Professional Service?
- ✅ Better deliverability
- ✅ No daily limits
- ✅ Analytics & tracking
- ✅ Bounce handling
- ✅ Dedicated IP
- ✅ 99.9% uptime

---

## 🎯 **Current Status**

✅ Email service implemented  
✅ 5 automated email types ready  
✅ Professional HTML templates  
✅ Works with ANY SMTP provider  
✅ Error handling included  
✅ Non-blocking implementation  

**Just add SMTP credentials and it works!**

---

## 📞 **Support**

If emails aren't working:
1. Check environment variables are set
2. Verify App Password is generated
3. Check logs for error messages
4. Test SMTP credentials with email client
5. Contact support: admin@smarthiring.com

---

## 🎉 **Quick Start (Copy-Paste)**

For Gmail (Most Common):

```bash
# 1. Generate Gmail App Password:
#    https://myaccount.google.com/apppasswords

# 2. Add to Render Environment Variables:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=youremail@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
FROM_EMAIL=youremail@gmail.com
FROM_NAME=Smart Hiring System
EMAIL_ENABLED=true
FRONTEND_URL=https://my-project-smart-hiring.onrender.com

# 3. Save & Deploy - Done! ✅
```

**Time to setup:** 5 minutes  
**Emails automated:** 5 types  
**Providers supported:** ALL of them!  

🚀 **Your automated email system is ready to use!**
