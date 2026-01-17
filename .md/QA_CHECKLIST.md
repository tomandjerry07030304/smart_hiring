# 📋 QA Checklist - Smart Hiring System

Use this checklist before every production deployment to ensure quality and stability.

---

## 🔐 Authentication & Security

### User Registration
- [ ] Register new candidate account
- [ ] Register new company account
- [ ] Verify email validation works
- [ ] Test password strength requirements
- [ ] Check duplicate email prevention
- [ ] Verify JWT token generation

### User Login
- [ ] Login with valid credentials
- [ ] Test invalid password rejection
- [ ] Test non-existent user handling
- [ ] Verify JWT token expiration (24h)
- [ ] Test logout functionality
- [ ] Check "remember me" functionality

### Authorization
- [ ] Candidate can only access candidate features
- [ ] Recruiter can only access recruiter features
- [ ] Admin has full access
- [ ] Verify role-based endpoint protection
- [ ] Test cross-user data access prevention

---

## 💼 Job Management

### Job Creation (Recruiter)
- [ ] Create job with all required fields
- [ ] Test validation for missing fields
- [ ] Verify skill tags save correctly
- [ ] Check job appears in job list
- [ ] Test job edit functionality
- [ ] Test job deletion (soft delete)

### Job Discovery (Candidate)
- [ ] Browse all open jobs
- [ ] Search jobs by keyword
- [ ] Filter by skills
- [ ] Filter by location
- [ ] View job details
- [ ] Check application count visibility

---

## 📝 Application Flow

### Application Submission
- [ ] Submit application to job
- [ ] Verify resume upload works
- [ ] Test duplicate application prevention
- [ ] Check application appears in "My Applications"
- [ ] Verify recruiter sees new application
- [ ] Test application count increments

### Application Status Updates (Recruiter)
- [ ] Update status to "Under Review"
- [ ] Update status to "Interview Scheduled"
- [ ] Update status to "Rejected"
- [ ] Update status to "Accepted"
- [ ] Verify candidate sees status change
- [ ] Check email notification sent

---

## 🧪 Assessment System

### Question Bank (Recruiter)
- [ ] Create multiple choice question
- [ ] Create true/false question
- [ ] Create short answer question
- [ ] Edit existing question
- [ ] Delete question (soft delete)
- [ ] Filter questions by category
- [ ] Filter questions by difficulty

### Quiz Management (Recruiter)
- [ ] Create quiz with selected questions
- [ ] Set duration and passing score
- [ ] Enable/disable randomization
- [ ] Set max attempts
- [ ] Link quiz to job
- [ ] View quiz analytics

### Quiz Taking (Candidate)
- [ ] Start quiz
- [ ] Answer questions
- [ ] See countdown timer
- [ ] Submit before time expires
- [ ] Test auto-submit on timeout
- [ ] View results immediately
- [ ] Check correct/incorrect feedback
- [ ] Verify score calculation accurate

---

## 📧 Email System

### Transactional Emails
- [ ] Welcome email on registration
- [ ] Application confirmation email
- [ ] Status change notification email
- [ ] Interview invitation email
- [ ] Verify email delivery to inbox
- [ ] Check email formatting (HTML)

### Email Preferences
- [ ] View current preferences
- [ ] Enable job alerts
- [ ] Disable newsletter
- [ ] Update marketing consent
- [ ] Verify opt-out respected
- [ ] Test preference persistence

---

## 🎨 UI/UX

### Loading States
- [ ] Skeleton screens appear on load
- [ ] Shimmer animation smooth
- [ ] Loading spinners for actions
- [ ] Progress indicators accurate

### Empty States
- [ ] "No jobs" message friendly
- [ ] "No applications" with CTA
- [ ] "No questions" prompt to create
- [ ] Empty quiz list helpful

### Toast Notifications
- [ ] Success toast (green)
- [ ] Error toast (red)
- [ ] Warning toast (yellow)
- [ ] Info toast (blue)
- [ ] Auto-dismiss works (5s)
- [ ] Close button functional
- [ ] Multiple toasts stack properly

### Responsive Design
- [ ] Mobile (320px - 767px)
- [ ] Tablet (768px - 1023px)
- [ ] Desktop (1024px+)
- [ ] Navigation menu responsive
- [ ] Forms adapt to screen size
- [ ] Tables scroll horizontally on mobile

---

## ♿ Accessibility

### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] Focus indicators visible
- [ ] Enter/Space activate buttons
- [ ] Escape closes modals
- [ ] Skip to main content works

### Screen Reader
- [ ] All images have alt text
- [ ] Form labels properly associated
- [ ] ARIA labels present
- [ ] Headings hierarchical (h1-h6)
- [ ] Error messages announced

### Color Contrast
- [ ] Text meets WCAG AA (4.5:1)
- [ ] Buttons meet WCAG AA
- [ ] Links distinguishable
- [ ] Error states clear

---

## ⚡ Performance

### Page Load Times
- [ ] Homepage < 2s
- [ ] Job list < 3s
- [ ] Quiz interface < 2s
- [ ] No layout shift (CLS)

### API Response Times
- [ ] Auth endpoints < 500ms
- [ ] Job list < 1s
- [ ] Application submission < 1s
- [ ] Quiz submission < 2s

### Caching
- [ ] Static assets cached
- [ ] API responses cached (appropriate)
- [ ] Redis cache hit rate > 70%

---

## 🔒 Security

### Input Validation
- [ ] XSS prevention works
- [ ] SQL injection prevented (NoSQL injection)
- [ ] File upload validation
- [ ] Rate limiting active

### Authentication Security
- [ ] Tokens expire properly
- [ ] Refresh token works
- [ ] Password hashing verified (bcrypt)
- [ ] Session management secure

### Data Protection
- [ ] PII encrypted at rest
- [ ] HTTPS enforced
- [ ] CORS configured correctly
- [ ] Security headers present

---

## 🗄️ Database

### Data Integrity
- [ ] Foreign key relationships maintained
- [ ] Indexes present on key fields
- [ ] No orphaned records
- [ ] Cascading deletes work

### Backup & Recovery
- [ ] Automated backup running
- [ ] Test restore from backup
- [ ] Point-in-time recovery works
- [ ] Backup retention policy set

---

## 📊 Monitoring & Logging

### Error Tracking
- [ ] Sentry capturing errors
- [ ] Error rates < 1%
- [ ] Critical errors alerted
- [ ] Stack traces captured

### Application Logs
- [ ] Structured logging active
- [ ] Log levels appropriate
- [ ] No sensitive data in logs
- [ ] Log rotation configured

### Metrics
- [ ] Response time metrics
- [ ] Error rate metrics
- [ ] Cache hit rate
- [ ] Database query performance

---

## 🚀 Deployment

### Pre-Deployment
- [ ] All tests passing (100%)
- [ ] No security vulnerabilities
- [ ] Database migrations ready
- [ ] Environment variables set
- [ ] Secrets rotated (if needed)

### Deployment Process
- [ ] Deploy to staging first
- [ ] Run smoke tests on staging
- [ ] Monitor staging for 1 hour
- [ ] Get approval from lead
- [ ] Deploy to production

### Post-Deployment
- [ ] Smoke tests pass
- [ ] Error rates normal
- [ ] Response times acceptable
- [ ] Monitor for 1 hour
- [ ] Verify new features work

---

## 🆘 Rollback Readiness

### Rollback Preparation
- [ ] Previous version tagged
- [ ] Database backup created
- [ ] Rollback script tested
- [ ] Team notified

### Rollback Triggers
- [ ] Error rate > 5%
- [ ] Critical feature broken
- [ ] Performance degradation > 50%
- [ ] Security vulnerability discovered

### Rollback Process
- [ ] Revert to previous version
- [ ] Restore database (if needed)
- [ ] Verify system stable
- [ ] Post-mortem scheduled

---

## ✅ Sign-Off

**Tested by:** ___________________________  
**Date:** ___________________________  
**Environment:** [ ] Staging  [ ] Production  
**Version:** ___________________________  

**Approval:**
- [ ] QA Lead
- [ ] Tech Lead
- [ ] Product Manager

**Notes:**
_______________________________________________________
_______________________________________________________
_______________________________________________________

---

## 📞 Emergency Contacts

- **On-Call Engineer:** [Phone/Slack]
- **Database Admin:** [Phone/Slack]
- **DevOps Lead:** [Phone/Slack]
- **Product Manager:** [Phone/Slack]

**Incident Response:** See `INCIDENT_RESPONSE.md`  
**Rollback Procedure:** See `ROLLBACK_GUIDE.md`
