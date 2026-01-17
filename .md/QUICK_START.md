# 🚀 Quick Start Guide

## Accessing the System

**URL**: http://localhost:5000

## User Roles & Credentials

### Admin
- **Email**: admin@smarthiring.com
- **Password**: changeme
- **Access**: Full platform control

### Test Company (Create your own)
1. Click "Company/Recruiter"
2. Click "Create Account"
3. Fill company details
4. Login after registration

### Test Candidate (Create your own)
1. Click "Candidate"
2. Click "Create Account"
3. Fill profile details
4. Login after registration

---

## Common Tasks

### As Admin:
1. Login → View dashboard statistics
2. Navigate to "Companies" → Approve new companies
3. Navigate to "Candidates" → View all registered candidates
4. Navigate to "Assessments" → Create skill tests (coming soon)

### As Company:
1. Login → View dashboard
2. Navigate to "My Jobs" → Click "Post New Job"
3. Fill job details → Submit
4. View applications from candidates
5. Review candidate profiles

### As Candidate:
1. Login → View dashboard
2. Navigate to "Browse Jobs" → Search/filter
3. Click job → View details → Apply
4. Navigate to "My Applications" → Track status
5. Navigate to "Assessments" → Take skill tests (coming soon)
6. Navigate to "Profile" → Update information

---

## File Structure

```
frontend/
├── index.html      # Main entry point
├── styles.css      # All styling (92KB)
├── app.js          # Core app & authentication
├── admin.js        # Admin dashboard
├── company.js      # Company dashboard
└── candidate.js    # Candidate dashboard
```

---

## Keyboard Shortcuts

- **F5**: Refresh page
- **F12**: Open developer console
- **Ctrl+Shift+Del**: Clear browser cache

---

## Quick Fixes

**Issue**: Login not working  
**Fix**: Check backend is running, verify credentials

**Issue**: Jobs not loading  
**Fix**: Refresh page, check browser console (F12)

**Issue**: Buttons not responding  
**Fix**: Clear cache, refresh page

**Issue**: Database error  
**Fix**: Restart MongoDB service

---

## API Testing

Test backend directly:
```powershell
# Health check
curl http://localhost:5000/api/health

# Login test
curl -X POST http://localhost:5000/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"admin@smarthiring.com","password":"changeme","role":"admin"}'
```

---

## Stop/Start System

### Stop Backend:
Press `Ctrl+C` in the terminal running Flask

### Start Backend:
```powershell
cd "c:\Users\venkat anand\OneDrive\Desktop\4-2\smart-hiring-system"
.\.venv\Scripts\Activate.ps1
cd backend
python app.py
```

### Restart MongoDB:
```powershell
Restart-Service MongoDB
```

---

## Support Checklist

Before reporting issues:
- [ ] Backend running (check terminal)
- [ ] MongoDB running (`Get-Service MongoDB`)
- [ ] Browser cache cleared
- [ ] JavaScript console checked (F12)
- [ ] Correct credentials used
- [ ] URL is http://localhost:5000

---

**Need Help?** Check `DEPLOYMENT_COMPLETE.md` for detailed documentation.
