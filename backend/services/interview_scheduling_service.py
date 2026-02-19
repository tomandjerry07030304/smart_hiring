"""
Interview Scheduling Service
Schedules, reschedules, and cancels interviews; persists records,
updates application status, and sends email notifications.
"""

import os
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from bson import ObjectId

from backend.models.database import get_db

logger = logging.getLogger(__name__)

SHORTLISTED_STATUSES = ("SHORTLISTED", "shortlisted", "Shortlisted")
INTERVIEW_SCHEDULED_STATUS = "INTERVIEW_SCHEDULED"
VALID_DURATIONS = (30, 45, 60, 90)


def _ensure_utc(dt: datetime) -> datetime:
    """Return datetime in UTC (naive UTC if input is naive)."""
    from datetime import timezone
    if dt.tzinfo:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


class InterviewServiceError(Exception):
    """Raised when interview operations fail."""
    pass


class InterviewSchedulingService:
    """Orchestrates interview scheduling, email notifications, and status updates."""

    def __init__(self) -> None:
        self._frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5000").rstrip("/")
        self._email_service = None

    @property
    def email_service(self):
        """Lazy-load email service to avoid circular imports."""
        if self._email_service is None:
            try:
                from backend.utils.email_service import email_service
                self._email_service = email_service
            except Exception:
                self._email_service = None
        return self._email_service

    def _generate_meeting_token(self) -> str:
        """Generate a secure meeting token."""
        return secrets.token_urlsafe(32)

    def _generate_meeting_link(self, token: str) -> str:
        """Generate a meeting link from a token."""
        return f"{self._frontend_url}/interview/room/{token}"

    def schedule_interview(
        self,
        application_id: str,
        scheduled_at: datetime,
        duration_minutes: int,
        panel_members: List[Dict[str, Any]],
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Schedule an interview for a shortlisted application.

        Args:
            application_id: Application document _id (string).
            scheduled_at: Interview start datetime.
            duration_minutes: 30, 45, 60, or 90.
            panel_members: List of dicts with user_id, email, name.
            notes: Optional notes for the interview.

        Returns:
            Interview document (as dict).

        Raises:
            InterviewServiceError: On validation failure.
        """
        db = get_db()
        applications = db["applications"]
        users = db["users"]
        jobs = db["jobs"]
        interviews = db["interviews"]

        # Validate duration
        if duration_minutes not in VALID_DURATIONS:
            raise InterviewServiceError("Duration must be 30, 45, 60, or 90 minutes")

        scheduled_at_utc = _ensure_utc(scheduled_at)
        if scheduled_at_utc <= datetime.utcnow():
            raise InterviewServiceError("Interview must be scheduled in the future")

        try:
            app_oid = ObjectId(application_id)
        except Exception:
            raise InterviewServiceError("Invalid application_id")

        application = applications.find_one({"_id": app_oid})
        if not application:
            raise InterviewServiceError("Application not found")

        status = application.get("status") or ""
        if status not in SHORTLISTED_STATUSES and status != INTERVIEW_SCHEDULED_STATUS:
            raise InterviewServiceError(
                f"Application must be shortlisted first (current status: {status})"
            )

        candidate_id = application.get("candidate_id")
        job_id = application.get("job_id")
        if not candidate_id or not job_id:
            raise InterviewServiceError("Application missing candidate_id or job_id")

        # Look up candidate user
        try:
            cand_oid = ObjectId(candidate_id) if isinstance(candidate_id, str) else candidate_id
        except Exception:
            raise InterviewServiceError("Invalid candidate_id")

        candidate = users.find_one({"_id": cand_oid})
        if not candidate:
            # Try string lookup
            candidate = users.find_one({"_id": candidate_id})

        job = jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise InterviewServiceError("Job not found")

        if not panel_members:
            raise InterviewServiceError("At least one panel member is required")

        # Resolve panel
        panel = []
        for p in panel_members:
            uid = p.get("user_id")
            email = p.get("email", "").strip()
            name = (p.get("name") or "").strip() or "Interviewer"
            if not uid:
                raise InterviewServiceError("Invalid panel member: missing user_id")
            panel.append({
                "user_id": str(uid),
                "email": email,
                "name": name,
                "role": p.get("role", "interviewer"),
            })

        # Generate meeting token and link
        meeting_token = self._generate_meeting_token()
        meeting_link = self._generate_meeting_link(meeting_token)

        candidate_name = (candidate or {}).get("full_name") or (candidate or {}).get("email", "Candidate")

        # Persist interview
        interview = {
            "_id": ObjectId(),
            "application_id": application_id,
            "job_id": str(job_id),
            "candidate_id": str(candidate_id),
            "scheduled_at": scheduled_at_utc,
            "duration_minutes": duration_minutes,
            "panel": panel,
            "meeting_token": meeting_token,
            "meeting_link": meeting_link,
            "status": "scheduled",
            "notes": notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        interviews.insert_one(interview)

        # Update application status
        applications.update_one(
            {"_id": app_oid},
            {
                "$set": {
                    "status": INTERVIEW_SCHEDULED_STATUS,
                    "interview_id": str(interview["_id"]),
                    "interview_scheduled": True,
                    "interview_date": scheduled_at_utc,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        # Send email notifications
        self._send_schedule_emails(
            candidate=candidate,
            candidate_name=candidate_name,
            job=job,
            interview=interview,
            panel=panel,
        )

        return _serialize_interview(interview)

    def _send_schedule_emails(self, candidate, candidate_name, job, interview, panel):
        """Send scheduling email notifications to candidate and panel."""
        if not self.email_service:
            logger.warning("Email service not available, skipping interview notifications")
            return

        job_title = job.get("title", "Position") if job else "Position"
        date_str = interview["scheduled_at"].strftime("%A, %B %d, %Y at %I:%M %p UTC")
        meeting_link = interview.get("meeting_link", "")

        # Notify candidate
        if candidate and candidate.get("email"):
            try:
                subject = f"Interview Scheduled - {job_title}"
                html = f"""
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                        <h1>🎉 Interview Scheduled!</h1>
                    </div>
                    <div style="padding: 30px;">
                        <p>Hi {candidate_name},</p>
                        <p>Your interview for <strong>{job_title}</strong> has been scheduled.</p>
                        <div style="background: #e0e7ff; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #667eea;">
                            <h3>Interview Details</h3>
                            <p><strong>Date & Time:</strong> {date_str}</p>
                            <p><strong>Duration:</strong> {interview['duration_minutes']} minutes</p>
                            <p><strong>Meeting Link:</strong> <a href="{meeting_link}">{meeting_link}</a></p>
                        </div>
                        <p>Please join the meeting a few minutes early. Good luck!</p>
                        <p>Best regards,<br>Smart Hiring Team</p>
                    </div>
                </body>
                </html>
                """
                self.email_service.send_email(candidate["email"], subject, html)
            except Exception as e:
                logger.error(f"Failed to send interview email to candidate: {e}")

        # Notify panel members
        for p in panel:
            if p.get("email"):
                try:
                    subject = f"Interview Panel Assignment - {job_title}"
                    html = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%); color: white; padding: 30px; text-align: center;">
                            <h1>📋 Interview Panel Assignment</h1>
                        </div>
                        <div style="padding: 30px;">
                            <p>Hi {p['name']},</p>
                            <p>You have been assigned as an interviewer for:</p>
                            <div style="background: #f0f0ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
                                <p><strong>Candidate:</strong> {candidate_name}</p>
                                <p><strong>Position:</strong> {job_title}</p>
                                <p><strong>Date & Time:</strong> {date_str}</p>
                                <p><strong>Duration:</strong> {interview['duration_minutes']} minutes</p>
                                <p><strong>Meeting Link:</strong> <a href="{meeting_link}">{meeting_link}</a></p>
                            </div>
                            <p>Best regards,<br>Smart Hiring Team</p>
                        </div>
                    </body>
                    </html>
                    """
                    self.email_service.send_email(p["email"], subject, html)
                except Exception as e:
                    logger.error(f"Failed to send interview email to panel member: {e}")

    def reschedule_interview(
        self,
        interview_id: str,
        new_datetime: datetime,
        duration_minutes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Reschedule an existing interview."""
        db = get_db()
        interviews = db["interviews"]
        users = db["users"]
        jobs = db["jobs"]

        try:
            ioid = ObjectId(interview_id)
        except Exception:
            raise InterviewServiceError("Invalid interview_id")

        interview = interviews.find_one({"_id": ioid})
        if not interview:
            raise InterviewServiceError("Interview not found")
        if interview.get("status") == "cancelled":
            raise InterviewServiceError("Cannot reschedule a cancelled interview")

        new_utc = _ensure_utc(new_datetime)
        if new_utc <= datetime.utcnow():
            raise InterviewServiceError("New time must be in the future")

        duration = duration_minutes if duration_minutes in VALID_DURATIONS else interview.get("duration_minutes", 60)

        # Generate new meeting token/link
        meeting_token = self._generate_meeting_token()
        meeting_link = self._generate_meeting_link(meeting_token)

        interviews.update_one(
            {"_id": ioid},
            {
                "$set": {
                    "scheduled_at": new_utc,
                    "duration_minutes": duration,
                    "meeting_token": meeting_token,
                    "meeting_link": meeting_link,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        # Update application
        app_id = interview.get("application_id")
        if app_id:
            db["applications"].update_one(
                {"_id": ObjectId(app_id)},
                {"$set": {"interview_date": new_utc, "updated_at": datetime.utcnow()}},
            )

        interview = interviews.find_one({"_id": ioid})

        # Send reschedule emails
        candidate_id = interview.get("candidate_id")
        candidate = users.find_one({"_id": ObjectId(candidate_id)}) if candidate_id else None
        job = jobs.find_one({"_id": ObjectId(interview.get("job_id", ""))}) if interview.get("job_id") else None
        candidate_name = (candidate or {}).get("full_name") or "Candidate"
        job_title = (job or {}).get("title", "Position")
        date_str = new_utc.strftime("%A, %B %d, %Y at %I:%M %p UTC")

        if self.email_service:
            recipients = []
            if candidate and candidate.get("email"):
                recipients.append({"email": candidate["email"], "name": candidate_name})
            for p in (interview.get("panel") or []):
                if p.get("email"):
                    recipients.append({"email": p["email"], "name": p.get("name", "Interviewer")})

            for r in recipients:
                try:
                    subject = f"Interview Rescheduled - {job_title}"
                    html = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 30px; text-align: center;">
                            <h1>📅 Interview Rescheduled</h1>
                        </div>
                        <div style="padding: 30px;">
                            <p>Hi {r['name']},</p>
                            <p>The interview for <strong>{job_title}</strong> has been rescheduled.</p>
                            <div style="background: #fef3c7; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                                <p><strong>New Date & Time:</strong> {date_str}</p>
                                <p><strong>Duration:</strong> {interview.get('duration_minutes')} minutes</p>
                                <p><strong>Meeting Link:</strong> <a href="{meeting_link}">{meeting_link}</a></p>
                            </div>
                            <p>Best regards,<br>Smart Hiring Team</p>
                        </div>
                    </body>
                    </html>
                    """
                    self.email_service.send_email(r["email"], subject, html)
                except Exception as e:
                    logger.error(f"Failed to send reschedule email: {e}")

        return _serialize_interview(interview)

    def cancel_interview(self, interview_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Cancel an interview and revert application status."""
        db = get_db()
        interviews = db["interviews"]
        applications = db["applications"]
        users = db["users"]
        jobs = db["jobs"]

        try:
            ioid = ObjectId(interview_id)
        except Exception:
            raise InterviewServiceError("Invalid interview_id")

        interview = interviews.find_one({"_id": ioid})
        if not interview:
            raise InterviewServiceError("Interview not found")

        if interview.get("status") == "cancelled":
            return _serialize_interview(interview)

        # Revert application status
        application_id = interview.get("application_id")
        if application_id:
            applications.update_one(
                {"_id": ObjectId(application_id)},
                {
                    "$set": {"status": "shortlisted", "updated_at": datetime.utcnow()},
                    "$unset": {"interview_id": "", "interview_scheduled": "", "interview_date": ""},
                },
            )

        interviews.update_one(
            {"_id": ioid},
            {
                "$set": {
                    "status": "cancelled",
                    "cancellation_reason": reason or "",
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        interview = interviews.find_one({"_id": ioid})

        # Send cancellation emails
        job = jobs.find_one({"_id": ObjectId(interview.get("job_id", ""))}) if interview.get("job_id") else None
        job_title = (job or {}).get("title", "Position")
        candidate_id = interview.get("candidate_id")
        candidate = users.find_one({"_id": ObjectId(candidate_id)}) if candidate_id else None
        scheduled_at = interview.get("scheduled_at")
        date_str = scheduled_at.strftime("%A, %B %d, %Y at %I:%M %p UTC") if scheduled_at else "the scheduled time"

        if self.email_service:
            recipients = []
            if candidate and candidate.get("email"):
                recipients.append({"email": candidate["email"], "name": (candidate or {}).get("full_name", "Candidate")})
            for p in (interview.get("panel") or []):
                if p.get("email"):
                    recipients.append({"email": p["email"], "name": p.get("name", "Interviewer")})

            for r in recipients:
                try:
                    subject = f"Interview Cancelled - {job_title}"
                    html = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 30px; text-align: center;">
                            <h1>❌ Interview Cancelled</h1>
                        </div>
                        <div style="padding: 30px;">
                            <p>Hi {r['name']},</p>
                            <p>The interview for <strong>{job_title}</strong> scheduled for {date_str} has been cancelled.</p>
                            {f'<p><strong>Reason:</strong> {reason}</p>' if reason else ''}
                            <p>We apologize for any inconvenience.</p>
                            <p>Best regards,<br>Smart Hiring Team</p>
                        </div>
                    </body>
                    </html>
                    """
                    self.email_service.send_email(r["email"], subject, html)
                except Exception as e:
                    logger.error(f"Failed to send cancellation email: {e}")

        return _serialize_interview(interview)

    def complete_interview(self, interview_id: str, feedback: Optional[str] = None) -> Dict[str, Any]:
        """Mark an interview as completed."""
        db = get_db()
        interviews = db["interviews"]

        try:
            ioid = ObjectId(interview_id)
        except Exception:
            raise InterviewServiceError("Invalid interview_id")

        interview = interviews.find_one({"_id": ioid})
        if not interview:
            raise InterviewServiceError("Interview not found")

        update = {
            "status": "completed",
            "updated_at": datetime.utcnow(),
        }
        if feedback:
            update["feedback"] = feedback

        interviews.update_one({"_id": ioid}, {"$set": update})

        # Update application status
        app_id = interview.get("application_id")
        if app_id:
            db["applications"].update_one(
                {"_id": ObjectId(app_id)},
                {"$set": {"status": "interviewed", "updated_at": datetime.utcnow()}},
            )

        return _serialize_interview(interviews.find_one({"_id": ioid}))

    def get_interview(self, interview_id: str) -> Optional[Dict[str, Any]]:
        """Get a single interview by ID."""
        db = get_db()
        try:
            interview = db["interviews"].find_one({"_id": ObjectId(interview_id)})
        except Exception:
            return None
        return _serialize_interview(interview) if interview else None

    def list_interviews_for_job(self, job_id: str) -> List[Dict[str, Any]]:
        """List all interviews for a specific job."""
        db = get_db()
        interviews = list(db["interviews"].find({"job_id": job_id}).sort("scheduled_at", -1))
        return [_serialize_interview(i) for i in interviews]

    def list_interviews_for_candidate(self, candidate_id: str) -> List[Dict[str, Any]]:
        """List all interviews for a candidate."""
        db = get_db()
        interviews = list(db["interviews"].find({"candidate_id": candidate_id}).sort("scheduled_at", -1))

        # Enrich with job info
        for interview in interviews:
            if interview.get("job_id"):
                job = db["jobs"].find_one({"_id": ObjectId(interview["job_id"])})
                if job:
                    interview["job_title"] = job.get("title", "Unknown Position")
                    interview["company"] = job.get("company", "")

        return [_serialize_interview(i) for i in interviews]

    def list_interviews_for_recruiter(self, recruiter_id: str) -> List[Dict[str, Any]]:
        """List all interviews where the recruiter's jobs are involved."""
        db = get_db()
        # Get recruiter's job IDs
        jobs = list(db["jobs"].find({"recruiter_id": recruiter_id}, {"_id": 1}))
        job_ids = [str(j["_id"]) for j in jobs]

        if not job_ids:
            return []

        interviews = list(
            db["interviews"]
            .find({"job_id": {"$in": job_ids}})
            .sort("scheduled_at", -1)
        )

        # Enrich with job and candidate info
        for interview in interviews:
            if interview.get("job_id"):
                job = db["jobs"].find_one({"_id": ObjectId(interview["job_id"])})
                if job:
                    interview["job_title"] = job.get("title", "Unknown")
            if interview.get("candidate_id"):
                try:
                    candidate = db["users"].find_one({"_id": ObjectId(interview["candidate_id"])})
                    if candidate:
                        interview["candidate_name"] = candidate.get("full_name", "Unknown")
                        interview["candidate_email"] = candidate.get("email", "")
                except Exception:
                    pass

        return [_serialize_interview(i) for i in interviews]


def _serialize_interview(doc: Optional[Dict]) -> Dict[str, Any]:
    """Convert interview document for JSON response (ObjectId and datetime to str)."""
    if not doc:
        return {}
    out = dict(doc)
    if "_id" in out:
        out["_id"] = str(out["_id"])
    for key in ("scheduled_at", "created_at", "updated_at"):
        if key in out and hasattr(out[key], "isoformat"):
            out[key] = out[key].isoformat()
    return out
