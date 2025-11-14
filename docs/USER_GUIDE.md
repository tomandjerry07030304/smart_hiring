# Smart Hiring System - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [First-Time Setup](#first-time-setup)
5. [Using the Application](#using-the-application)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

## Introduction

Smart Hiring System is an AI-powered recruitment platform that helps organizations make fair, data-driven hiring decisions. The system provides:

- **Resume Parsing**: Automatically extract information from resumes (PDF, DOCX, DOC formats)
- **Intelligent Matching**: ML-powered candidate-job matching algorithms
- **Bias Detection**: Fairness audits to ensure unbiased hiring practices
- **Resume Anonymization**: Remove personally identifiable information for blind screening
- **Assessment Management**: Create and manage various types of assessments

## System Requirements

### Windows
- **OS**: Windows 10 (64-bit) or later
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk Space**: 2 GB free space
- **Database**: MongoDB (can use cloud Atlas or local installation)

### Optional Requirements
- Internet connection (for MongoDB Atlas)
- Modern web browser (Chrome, Firefox, Edge)

## Installation

### Option 1: Windows Installer (Recommended)

1. **Download the installer**
   - Download `SmartHiringSystem-Setup-v1.0.0.exe` from the releases page

2. **Run the installer**
   - Double-click the installer
   - Follow the installation wizard
   - Choose installation directory (default: `C:\Program Files\SmartHiringSystem`)
   - Select components:
     - ☑ Core Application (required)
     - ☐ Local MongoDB (optional - install if you don't have MongoDB)
     - ☑ Desktop Shortcut
     - ☑ Start Menu Shortcut

3. **Complete installation**
   - Click "Install"
   - Wait for installation to complete
   - Click "Finish"

### Option 2: Docker Installation

```powershell
# 1. Clone or download the project
git clone https://github.com/your-org/smart-hiring-system.git
cd smart-hiring-system

# 2. Configure environment
cp .env.template .env
# Edit .env with your settings

# 3. Start with Docker Compose
cd deploy
docker-compose up -d

# 4. Access the application
# Open http://localhost:3000 in your browser
```

### Option 3: Portable ZIP

1. Download `smart-hiring-system-v1.0.0.zip`
2. Extract to your desired location
3. Run `start_windows.bat`

## First-Time Setup

### Configuration Wizard

When you launch the application for the first time, you'll see the configuration wizard:

#### Step 1: Database Configuration

Choose your database option:

**Option A: MongoDB Atlas (Cloud - Recommended)**
1. Select "Cloud MongoDB"
2. Enter your MongoDB Atlas connection string:
   ```
   mongodb+srv://<username>:<password>@cluster.mongodb.net/smart_hiring_db
   ```
3. Click "Test Connection"
4. Click "Next" when connection succeeds

**Option B: Local MongoDB**
1. Select "Local MongoDB"
2. Ensure MongoDB is installed (installer can do this for you)
3. Default connection: `mongodb://localhost:27017/smart_hiring_db`
4. Click "Test Connection"
5. Click "Next"

#### Step 2: Admin Account Setup

1. Change the default admin password
   - Default username: `admin@smarthiring.com`
   - **Important**: Change the default password!
   - Create a strong password (min 8 characters)

2. Enter admin details:
   - Full Name
   - Email (for notifications)
   - Phone (optional)

#### Step 3: Feature Configuration

Enable/disable features:
- ☑ **ML-Powered Matching**: Use machine learning for candidate matching
- ☑ **Resume Anonymization**: Remove PII for blind screening
- ☑ **Fairness Audits**: Monitor hiring decisions for bias
- ☐ **Email Notifications**: Send automated emails (requires SMTP setup)

#### Step 4: SMTP Configuration (Optional)

If you enabled email notifications:
1. SMTP Server: e.g., `smtp.gmail.com`
2. Port: `587` (TLS) or `465` (SSL)
3. Username: Your email
4. Password: Your email password or app password
5. From Address: e.g., `noreply@yourcompany.com`

#### Step 5: Complete Setup

1. Review your configuration
2. Click "Initialize Database"
3. Wait for database setup to complete
4. Click "Launch Application"

## Using the Application

### Dashboard Overview

After logging in, you'll see the main dashboard with:
- **Total Jobs**: Active job postings
- **Total Candidates**: Registered candidates
- **Pending Applications**: Applications awaiting review
- **This Month's Hires**: Recent hiring statistics

### For Recruiters

#### Creating a Job Posting

1. Navigate to **Jobs** > **Create New Job**
2. Fill in job details:
   - Job Title
   - Description
   - Requirements
   - Skills (comma-separated)
   - Location
   - Salary Range
   - Employment Type
3. Click **Publish Job**

#### Reviewing Applications

1. Go to **Applications**
2. Select a job posting
3. View candidate matches with AI scores:
   - **Match Score**: Overall compatibility (0-100%)
   - **Skill Match**: Required skills match percentage
   - **Experience Match**: Years of experience alignment
4. Actions:
   - **View Resume**: See full resume
   - **View Anonymized**: See PII-removed version
   - **Schedule Interview**: Send interview invitation
   - **Reject**: Send rejection notification
   - **Shortlist**: Move to next round

#### Running Fairness Audits

1. Navigate to **Dashboard** > **Fairness Audits**
2. Select time period or specific jobs
3. Click **Run Audit**
4. Review audit report:
   - Demographic analysis
   - Bias indicators
   - Recommendations
5. Generate transparency report

### For Candidates

#### Creating Your Profile

1. Register at **Sign Up**
2. Fill in your details:
   - Name
   - Email
   - Phone
   - Skills
   - Education
   - Experience
3. Upload your resume (PDF, DOCX, DOC)

#### Browsing Jobs

1. Go to **Jobs** > **Browse**
2. Use filters:
   - Location
   - Job Type
   - Salary Range
   - Skills
3. View job details
4. Click **Apply** to submit application

#### Tracking Applications

1. Navigate to **My Applications**
2. View status:
   - **Submitted**: Application received
   - **Under Review**: Being reviewed by recruiter
   - **Interview Scheduled**: Invitation sent
   - **Rejected**: Application declined
   - **Hired**: Offer extended
3. View timeline and notes

#### Taking Assessments

1. When invited, go to **Assessments**
2. Select the assessment
3. Complete questions:
   - **MCQ**: Multiple choice questions
   - **Coding**: Programming challenges
   - **Behavioral**: Situational questions
4. Submit before deadline

### For Administrators

#### Managing Users

1. Go to **Admin** > **Users**
2. View all users (Admins, Recruiters, Candidates)
3. Actions:
   - **Edit**: Modify user details
   - **Deactivate**: Disable account
   - **Delete**: Remove user
   - **Reset Password**: Send reset link

#### System Configuration

1. Navigate to **Admin** > **Settings**
2. Configure:
   - Upload limits
   - Rate limits
   - Feature toggles
   - SMTP settings
   - Database settings

#### Viewing Logs

1. Go to **Admin** > **System Logs**
2. Filter by:
   - Date range
   - Log level (INFO, WARNING, ERROR)
   - Module
3. Download logs for analysis

#### Database Backup

1. Navigate to **Admin** > **Maintenance**
2. Click **Backup Database**
3. Choose backup location
4. Wait for completion
5. Store backup securely

## Troubleshooting

### Application Won't Start

**Problem**: Application doesn't launch after installation

**Solutions**:
1. Check if MongoDB is running:
   ```powershell
   Get-Service MongoDB
   ```
2. Verify port 8000 is available:
   ```powershell
   netstat -ano | findstr :8000
   ```
3. Check logs at: `C:\Program Files\SmartHiringSystem\logs\app.log`
4. Restart the application

### Database Connection Failed

**Problem**: Can't connect to MongoDB

**Solutions**:
1. **For Local MongoDB**:
   - Ensure MongoDB service is running
   - Check connection string in `.env`
   - Verify port 27017 is accessible

2. **For MongoDB Atlas**:
   - Check internet connection
   - Verify connection string is correct
   - Ensure IP whitelist includes your IP
   - Check cluster is running

### Resume Upload Fails

**Problem**: Can't upload resume files

**Solutions**:
1. Check file size (must be < 10 MB)
2. Verify file format (PDF, DOCX, DOC only)
3. Ensure upload folder has write permissions
4. Check disk space availability

### ML Features Not Working

**Problem**: Matching scores not calculated

**Solutions**:
1. Ensure ML models are present in `ml_models/` directory
2. Check `ENABLE_ML_FEATURES=true` in `.env`
3. Verify sufficient RAM (4GB+)
4. Check logs for model loading errors

### Email Notifications Not Sending

**Problem**: Emails not being sent

**Solutions**:
1. Verify SMTP settings in configuration
2. Check `ENABLE_EMAIL_NOTIFICATIONS=true`
3. Test SMTP connection:
   ```python
   python scripts/test_smtp.py
   ```
4. Check email service allows third-party apps
5. Use app-specific password for Gmail

## FAQ

### General Questions

**Q: Is my data secure?**
A: Yes. All passwords are hashed with bcrypt, and sensitive data is encrypted. We recommend using HTTPS in production.

**Q: Can I use this offline?**
A: Yes, with local MongoDB installation. Some features like email notifications require internet.

**Q: How many users can the system handle?**
A: The system can handle thousands of users. Performance depends on your hardware and database configuration.

### Installation Questions

**Q: Do I need to install MongoDB separately?**
A: No, the installer can install MongoDB for you, or you can use MongoDB Atlas (cloud).

**Q: Can I install on Windows Server?**
A: Yes, Windows Server 2016 or later is supported.

**Q: How much disk space is needed?**
A: Minimum 2 GB, but plan for more if storing many resumes (approximately 1 MB per resume).

### Usage Questions

**Q: What resume formats are supported?**
A: PDF, DOCX, DOC, and TXT formats.

**Q: How are matching scores calculated?**
A: Using TF-IDF similarity, skill matching, and experience alignment algorithms.

**Q: Can I customize the matching algorithm?**
A: Yes, admins can adjust weights in the configuration.

**Q: How long are resumes stored?**
A: Indefinitely by default. Admins can configure retention policies.

### Technical Questions

**Q: What programming languages is it built with?**
A: Backend: Python (Flask), Frontend: React, Database: MongoDB

**Q: Can I integrate with my ATS?**
A: Yes, via REST API. See API_DOCUMENTATION.md for details.

**Q: Is there a mobile app?**
A: Not yet, but the web interface is mobile-responsive.

**Q: How do I update to a new version?**
A: Download the new installer and run it. Your data will be preserved.

## Getting Help

### Support Channels

- **Documentation**: Check ADMIN_GUIDE.md and DEVELOPER_GUIDE.md
- **GitHub Issues**: Report bugs or request features
- **Email Support**: support@smarthiring.com (if configured)
- **Community Forum**: community.smarthiring.com (if available)

### Reporting Bugs

When reporting issues, include:
1. Version number (Help > About)
2. Operating system and version
3. Steps to reproduce
4. Error messages or screenshots
5. Relevant log files

## Appendix

### Keyboard Shortcuts

- `Ctrl+N`: New Job Posting
- `Ctrl+F`: Search
- `Ctrl+S`: Save
- `Alt+D`: Dashboard
- `Alt+J`: Jobs
- `Alt+C`: Candidates
- `Alt+A`: Applications

### File Locations

- **Installation**: `C:\Program Files\SmartHiringSystem\`
- **Logs**: `%PROGRAMDATA%\SmartHiringSystem\logs\`
- **Config**: `%PROGRAMDATA%\SmartHiringSystem\.env`
- **Uploads**: `%PROGRAMDATA%\SmartHiringSystem\uploads\`

### Supported Browsers

- Google Chrome 90+
- Mozilla Firefox 88+
- Microsoft Edge 90+
- Safari 14+ (macOS)

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-14  
**License**: MIT
