"""
Video Interview Service
=======================
Manages video interview sessions including:
- Meeting link generation with secure tokens
- Session lifecycle management (schedule → join → record → complete)
- Webcam/audio detection tracking
- Recording metadata storage
- Integration with AI Interviewer V2 for question generation & answer evaluation
- Email invitations and WebSocket notifications
- Timezone-aware scheduling
- Video recording download for both candidate and interviewer
- Live interview session support (WebRTC signaling)
- Anti-malpractice event logging

DB Collection: 'video_interviews'
"""

import os
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from bson import ObjectId

from backend.models.database import get_db

logger = logging.getLogger(__name__)

# ─── Constants ──────────────────────────────────────────────────────────────────

TOKEN_LENGTH = 32                    # bytes → 43-char URL-safe string
DEFAULT_EXPIRY_HOURS = 48            # link expires after 48 hours
MAX_RECORDING_SIZE_MB = 500          # per-session cap
SUPPORTED_MEDIA_TYPES = ['video/webm', 'video/mp4', 'audio/webm', 'audio/ogg']

# Upload directory for recordings
RECORDINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'recordings')

SESSION_STATUSES = [
    'scheduled',       # invitation sent, not yet joined
    'waiting',         # candidate opened the link, waiting to start
    'in_progress',     # interview actively running
    'paused',          # temporarily paused (e.g., network issue)
    'completed',       # candidate finished all questions
    'expired',         # link expired before candidate joined
    'cancelled',       # recruiter cancelled
]

# Supported timezones with UTC offsets (hours)
TIMEZONE_OFFSETS = {
    'UTC': 0,
    'GMT': 0,
    'IST': 5.5,      # India Standard Time
    'EST': -5,        # Eastern Standard Time
    'EDT': -4,        # Eastern Daylight Time
    'CST': -6,        # Central Standard Time
    'CDT': -5,        # Central Daylight Time
    'MST': -7,        # Mountain Standard Time
    'MDT': -6,        # Mountain Daylight Time
    'PST': -8,        # Pacific Standard Time
    'PDT': -7,        # Pacific Daylight Time
    'CET': 1,         # Central European Time
    'CEST': 2,        # Central European Summer Time
    'JST': 9,         # Japan Standard Time
    'AEST': 10,       # Australian Eastern Standard Time
    'AEDT': 11,       # Australian Eastern Daylight Time
    'SGT': 8,         # Singapore Time
    'CST_CN': 8,      # China Standard Time
    'KST': 9,         # Korea Standard Time
    'GST': 4,         # Gulf Standard Time (Dubai)
}


# ─── Timezone Helpers ───────────────────────────────────────────────────────────

def convert_utc_to_timezone(utc_dt: datetime, tz_name: str) -> Tuple[datetime, str]:
    """
    Convert a UTC datetime to the requested timezone.
    Returns (converted_datetime, display_string).
    """
    offset_hours = TIMEZONE_OFFSETS.get(tz_name.upper(), 0)
    offset = timedelta(hours=offset_hours)
    local_dt = utc_dt + offset
    display = local_dt.strftime('%B %d, %Y at %I:%M %p') + f' ({tz_name.upper()})'
    return local_dt, display


def convert_timezone_to_utc(local_dt: datetime, tz_name: str) -> datetime:
    """Convert a local datetime in the given timezone to UTC."""
    offset_hours = TIMEZONE_OFFSETS.get(tz_name.upper(), 0)
    return local_dt - timedelta(hours=offset_hours)


# ─── Token & Link Management ───────────────────────────────────────────────────

def generate_meeting_token() -> str:
    """
    Generate a cryptographically secure meeting token.
    Returns a 43-character URL-safe string (256-bit entropy).
    """
    return secrets.token_urlsafe(TOKEN_LENGTH)


def generate_meeting_link(base_url: str, token: str) -> str:
    """Build the full meeting URL from base URL and token."""
    base_url = base_url.rstrip('/')
    return f"{base_url}/interview/room/{token}"


# ─── Session CRUD ──────────────────────────────────────────────────────────────

def create_interview_session(
    job_id: str,
    candidate_id: str,
    scheduled_by: str,
    interview_type: str = 'ai_automated',
    duration_minutes: int = 90,
    expiry_hours: int = DEFAULT_EXPIRY_HOURS,
    questions: Optional[List[Dict]] = None,
    base_url: str = 'http://localhost:5000',
    scheduled_time_utc: Optional[datetime] = None,
    candidate_timezone: str = 'UTC',
    interviewer_id: Optional[str] = None,
) -> Dict:
    """
    Create a new video interview session.

    Args:
        job_id:             ObjectId string of the job
        candidate_id:       ObjectId string of the candidate / applicant user
        scheduled_by:       ObjectId string of the recruiter / admin who scheduled
        interview_type:     'ai_automated' | 'live' | 'hybrid'
        duration_minutes:   expected total duration
        expiry_hours:       hours until the meeting link expires
        questions:          pre-generated question list (optional)
        base_url:           application base URL for link building
        scheduled_time_utc: when the interview should happen (None = ASAP)
        candidate_timezone: candidate's timezone (e.g., 'IST', 'EST', 'PST')
        interviewer_id:     ObjectId string of the interviewer (for live interviews)

    Returns:
        The inserted session document (dict).
    """
    db = get_db()

    token = generate_meeting_token()
    meeting_link = generate_meeting_link(base_url, token)
    now = datetime.utcnow()

    # Compute scheduled time display in candidate's timezone
    sched_utc = scheduled_time_utc or now
    _, scheduled_display = convert_utc_to_timezone(sched_utc, candidate_timezone)

    session_doc = {
        'job_id': ObjectId(job_id),
        'candidate_id': ObjectId(candidate_id),
        'scheduled_by': ObjectId(scheduled_by),
        'interviewer_id': ObjectId(interviewer_id) if interviewer_id else None,
        'interview_type': interview_type,          # ai_automated | live | hybrid
        'status': 'scheduled',
        'token': token,
        'meeting_link': meeting_link,

        # Timing & Timezone
        'duration_minutes': duration_minutes,
        'expires_at': now + timedelta(hours=expiry_hours),
        'scheduled_at': now,
        'scheduled_time_utc': sched_utc,
        'candidate_timezone': candidate_timezone.upper(),
        'scheduled_time_display': scheduled_display,
        'started_at': None,
        'completed_at': None,

        # Questions & answers
        'questions': questions or [],
        'answers': [],
        'current_question_index': 0,

        # Media
        'webcam_detected': False,
        'audio_detected': False,
        'recordings': [],

        # Scoring
        'overall_score': None,
        'section_scores': {},
        'ai_evaluation': None,

        # Anti-malpractice
        'malpractice_events': [],       # tab switches, multiple screens, face loss etc
        'malpractice_score': 0,         # 0 = clean, higher = more suspicious

        # Live interview fields
        'interviewer_joined': False,
        'candidate_joined': False,

        # Metadata
        'created_at': now,
        'updated_at': now,
    }

    result = db['video_interviews'].insert_one(session_doc)
    session_doc['_id'] = result.inserted_id

    logger.info(
        "Created video interview session %s for candidate %s, job %s",
        result.inserted_id, candidate_id, job_id,
    )
    return session_doc


def get_session_by_token(token: str) -> Optional[Dict]:
    """Look up a session by its meeting token. Returns None if not found."""
    db = get_db()
    return db['video_interviews'].find_one({'token': token})


def get_session_by_id(session_id: str) -> Optional[Dict]:
    """Look up a session by its _id."""
    db = get_db()
    return db['video_interviews'].find_one({'_id': ObjectId(session_id)})


def get_sessions_for_candidate(candidate_id: str) -> List[Dict]:
    """Return all sessions for a given candidate, newest first."""
    db = get_db()
    return list(
        db['video_interviews']
        .find({'candidate_id': ObjectId(candidate_id)})
        .sort('scheduled_at', -1)
    )


def get_sessions_for_job(job_id: str) -> List[Dict]:
    """Return all sessions for a given job, newest first."""
    db = get_db()
    return list(
        db['video_interviews']
        .find({'job_id': ObjectId(job_id)})
        .sort('scheduled_at', -1)
    )


# ─── Session State Transitions ─────────────────────────────────────────────────

def _update_session(session_id, update_fields: Dict) -> Optional[Dict]:
    """Apply $set update and return the updated document."""
    db = get_db()
    update_fields['updated_at'] = datetime.utcnow()
    result = db['video_interviews'].find_one_and_update(
        {'_id': ObjectId(session_id)},
        {'$set': update_fields},
        return_document=True,                      # pymongo.ReturnDocument.AFTER
    )
    return result


def join_session(token: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Candidate opens the meeting link.

    Returns:
        (session_doc, error_message)
        On success error_message is None.
    """
    session = get_session_by_token(token)
    if not session:
        return None, 'Interview session not found.'

    if session['status'] == 'cancelled':
        return None, 'This interview has been cancelled.'

    if session['status'] == 'completed':
        return None, 'This interview has already been completed.'

    now = datetime.utcnow()
    if now > session['expires_at']:
        _update_session(str(session['_id']), {'status': 'expired'})
        return None, 'This interview link has expired.'

    if session['status'] in ('scheduled', 'paused'):
        session = _update_session(str(session['_id']), {'status': 'waiting'})

    return session, None


def start_interview(session_id: str) -> Optional[Dict]:
    """Transition session from 'waiting' → 'in_progress'."""
    return _update_session(session_id, {
        'status': 'in_progress',
        'started_at': datetime.utcnow(),
    })


def pause_interview(session_id: str) -> Optional[Dict]:
    """Pause an in-progress interview."""
    return _update_session(session_id, {'status': 'paused'})


def resume_interview(session_id: str) -> Optional[Dict]:
    """Resume a paused interview."""
    return _update_session(session_id, {'status': 'in_progress'})


def complete_interview(session_id: str, overall_score: Optional[float] = None) -> Optional[Dict]:
    """Mark session as completed and optionally record overall score."""
    update = {
        'status': 'completed',
        'completed_at': datetime.utcnow(),
    }
    if overall_score is not None:
        update['overall_score'] = overall_score
    return _update_session(session_id, update)


def cancel_interview(session_id: str, reason: str = '') -> Optional[Dict]:
    """Cancel a scheduled or waiting interview."""
    return _update_session(session_id, {
        'status': 'cancelled',
        'cancel_reason': reason,
    })


# ─── Webcam & Audio ────────────────────────────────────────────────────────────

def update_media_status(
    session_id: str,
    webcam_detected: Optional[bool] = None,
    audio_detected: Optional[bool] = None,
) -> Optional[Dict]:
    """Update webcam / microphone detection flags."""
    update: Dict = {}
    if webcam_detected is not None:
        update['webcam_detected'] = webcam_detected
    if audio_detected is not None:
        update['audio_detected'] = audio_detected
    if not update:
        return get_session_by_id(session_id)
    return _update_session(session_id, update)


# ─── Answer Submission ──────────────────────────────────────────────────────────

def submit_answer(
    session_id: str,
    question_index: int,
    answer_text: str,
    evaluation: Optional[Dict] = None,
) -> Optional[Dict]:
    """
    Record a candidate's answer and its AI evaluation.

    Args:
        session_id:      session ObjectId string
        question_index:  0-based index into session['questions']
        answer_text:     candidate's textual answer (or transcription)
        evaluation:      dict from evaluate_answer_advanced() — optional

    Returns:
        Updated session document.
    """
    db = get_db()
    now = datetime.utcnow()

    answer_doc = {
        'question_index': question_index,
        'answer_text': answer_text,
        'evaluation': evaluation,
        'submitted_at': now,
    }

    result = db['video_interviews'].find_one_and_update(
        {'_id': ObjectId(session_id)},
        {
            '$push': {'answers': answer_doc},
            '$set': {
                'current_question_index': question_index + 1,
                'updated_at': now,
            },
        },
        return_document=True,
    )
    return result


# ─── Recording Metadata ────────────────────────────────────────────────────────

def add_recording_metadata(
    session_id: str,
    filename: str,
    size_bytes: int,
    media_type: str,
    storage_path: str = '',
) -> Optional[Dict]:
    """
    Append recording metadata to the session.

    Actual binary storage is handled externally (local filesystem or object store).
    This method only tracks the metadata in the DB.
    """
    if media_type not in SUPPORTED_MEDIA_TYPES:
        logger.warning("Unsupported media type '%s' for session %s", media_type, session_id)

    db = get_db()
    recording = {
        'filename': filename,
        'size_bytes': size_bytes,
        'media_type': media_type,
        'storage_path': storage_path,
        'uploaded_at': datetime.utcnow(),
    }

    result = db['video_interviews'].find_one_and_update(
        {'_id': ObjectId(session_id)},
        {
            '$push': {'recordings': recording},
            '$set': {'updated_at': datetime.utcnow()},
        },
        return_document=True,
    )
    return result


# ─── AI Integration Helpers ─────────────────────────────────────────────────────

def generate_questions_for_session(
    session_id: str,
    job: Dict,
    candidate: Optional[Dict] = None,
    num_questions: int = 25,
) -> Optional[Dict]:
    """
    Generate AI interview questions via the V2 service and attach them to the session.
    """
    from backend.services.ai_interviewer_service_v2 import (
        generate_interview_questions,
        create_interview_schedule,
    )

    questions = generate_interview_questions(
        job=job,
        candidate=candidate,
        num_questions=num_questions,
        include_behavioral=True,
    )

    schedule = create_interview_schedule(
        questions=questions,
        total_duration_minutes=90,
        include_breaks=True,
    )

    return _update_session(session_id, {
        'questions': questions,
        'schedule': schedule,
    })


def evaluate_session_answers(session_id: str) -> Optional[Dict]:
    """
    Run AI evaluation on all submitted answers and compute an overall score.
    """
    from backend.services.ai_interviewer_service_v2 import evaluate_answer

    session = get_session_by_id(session_id)
    if not session:
        return None

    questions = session.get('questions', [])
    answers = session.get('answers', [])
    total_score = 0
    max_total = 0
    evaluated_answers = []

    for ans in answers:
        q_idx = ans.get('question_index', 0)
        if q_idx < len(questions):
            question = questions[q_idx]
            evaluation = evaluate_answer(question, ans.get('answer_text', ''))
            ans_copy = dict(ans)
            ans_copy['evaluation'] = evaluation
            evaluated_answers.append(ans_copy)
            total_score += evaluation.get('score', 0)
            max_total += evaluation.get('max_score', 10)
        else:
            evaluated_answers.append(ans)

    overall_pct = round((total_score / max_total * 100), 2) if max_total > 0 else 0.0

    return _update_session(session_id, {
        'answers': evaluated_answers,
        'overall_score': overall_pct,
        'ai_evaluation': {
            'total_score': total_score,
            'max_total': max_total,
            'percentage': overall_pct,
            'evaluated_at': datetime.utcnow(),
        },
    })


# ─── Email Invitation Helper ───────────────────────────────────────────────────

def send_interview_invitation(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    company_name: str,
    meeting_link: str,
    scheduled_date: Optional[str] = None,
    duration_minutes: int = 90,
    scheduled_time_display: Optional[str] = None,
    candidate_timezone: str = 'UTC',
) -> bool:
    """
    Send a video interview invitation email to the candidate.
    Includes timezone-aware scheduled time display.
    Returns True on success, False on failure.
    """
    try:
        from backend.utils.email_service import EmailService
        email_service = EmailService()

        # Use the timezone-aware display if available
        if scheduled_time_display:
            date_display = scheduled_time_display
        elif scheduled_date:
            date_display = scheduled_date
        else:
            date_display = 'at your earliest convenience'

        subject = f"Video Interview Invitation — {job_title} at {company_name}"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2563eb;">Video Interview Invitation</h2>
            <p>Dear {candidate_name},</p>
            <p>You have been invited to a video interview for the position of
               <strong>{job_title}</strong> at <strong>{company_name}</strong>.</p>

            <div style="background: #f0f9ff; border-left: 4px solid #2563eb;
                        padding: 16px; margin: 20px 0; border-radius: 4px;">
                <p style="margin: 4px 0;"><strong>Position:</strong> {job_title}</p>
                <p style="margin: 4px 0;"><strong>Duration:</strong> ~{duration_minutes} minutes ({duration_minutes // 25}-{duration_minutes // 20 + 1} questions)</p>
                <p style="margin: 4px 0;"><strong>Scheduled:</strong> {date_display}</p>
                <p style="margin: 4px 0;"><strong>Your Timezone:</strong> {candidate_timezone.upper()}</p>
            </div>

            <p>Click the button below to join your interview session:</p>
            <a href="{meeting_link}"
               style="display: inline-block; background: #2563eb; color: #fff;
                      padding: 12px 32px; text-decoration: none; border-radius: 6px;
                      font-weight: bold; margin: 12px 0;">
                Join Interview
            </a>

            <div style="background: #fffbeb; border-left: 4px solid #f59e0b;
                        padding: 12px; margin: 20px 0; border-radius: 4px;">
                <p style="margin: 4px 0; font-weight: bold; color: #92400e;">Before you join:</p>
                <ul style="margin: 8px 0; padding-left: 20px; color: #78350f;">
                    <li>Ensure you have a stable internet connection</li>
                    <li>Use a quiet, well-lit room</li>
                    <li>Have a working webcam and microphone</li>
                    <li>Use Google Chrome or Mozilla Firefox for best experience</li>
                    <li>Keep your government ID ready for verification</li>
                </ul>
            </div>

            <p style="color: #6b7280; font-size: 13px; margin-top: 24px;">
                This link will expire 48 hours after it was generated.<br>
                <strong>Important:</strong> Do not share this link with anyone else.
                Tab switching and other malpractice will be monitored during the interview.
            </p>

            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
            <p style="color: #9ca3af; font-size: 12px;">
                Smart Hiring Platform — AI-Powered Recruitment
            </p>
        </div>
        """

        return email_service.send_email(candidate_email, subject, html_content)

    except Exception as e:
        logger.error("Failed to send interview invitation to %s: %s", candidate_email, e)
        return False


# ─── WebSocket Notification Helper ──────────────────────────────────────────────

def notify_interview_scheduled_ws(candidate_user_id: str, session_doc: Dict) -> bool:
    """
    Push a real-time notification to the candidate via WebSocket.
    Wraps the existing WebSocketManager.notify_interview_scheduled().
    """
    try:
        from backend.services.websocket_service import get_websocket_manager
        ws = get_websocket_manager()
        if ws is None:
            logger.warning("WebSocket manager not initialised — skipping notification.")
            return False

        interview_data = {
            'session_id': str(session_doc.get('_id', '')),
            'meeting_link': session_doc.get('meeting_link', ''),
            'job_id': str(session_doc.get('job_id', '')),
            'status': session_doc.get('status', 'scheduled'),
            'expires_at': session_doc['expires_at'].isoformat() if session_doc.get('expires_at') else None,
            'duration_minutes': session_doc.get('duration_minutes', 60),
        }
        return ws.notify_interview_scheduled(candidate_user_id, interview_data)

    except Exception as e:
        logger.error("WebSocket notification failed for user %s: %s", candidate_user_id, e)
        return False


# ─── Anti-Malpractice Event Logging ─────────────────────────────────────────────

def log_malpractice_event(
    session_id: str,
    event_type: str,
    details: Optional[Dict] = None,
) -> Optional[Dict]:
    """
    Log an anti-malpractice event (tab switch, face loss, multiple screens, etc.).
    Increments the malpractice score.

    event_type: 'tab_switch' | 'face_not_detected' | 'multiple_screens' |
                'copy_paste' | 'right_click' | 'devtools_open' | 'browser_resize'
    """
    db = get_db()
    now = datetime.utcnow()

    severity_map = {
        'tab_switch': 3,
        'face_not_detected': 2,
        'multiple_screens': 5,
        'copy_paste': 4,
        'right_click': 1,
        'devtools_open': 5,
        'browser_resize': 1,
    }
    severity = severity_map.get(event_type, 2)

    event = {
        'event_type': event_type,
        'severity': severity,
        'details': details or {},
        'timestamp': now,
    }

    result = db['video_interviews'].find_one_and_update(
        {'_id': ObjectId(session_id)},
        {
            '$push': {'malpractice_events': event},
            '$inc': {'malpractice_score': severity},
            '$set': {'updated_at': now},
        },
        return_document=True,
    )
    if result:
        logger.warning(
            "Malpractice event '%s' (severity=%d) for session %s — total score: %d",
            event_type, severity, session_id, result.get('malpractice_score', 0),
        )
    return result


# ─── Video Recording Storage & Download ─────────────────────────────────────────

def save_recording_file(
    session_id: str,
    file_data,
    filename: str,
    media_type: str = 'video/webm',
) -> Tuple[Optional[str], Optional[str]]:
    """
    Save an uploaded recording file to disk and record metadata.

    Args:
        session_id: the interview session ObjectId string
        file_data:  file-like object or bytes
        filename:   original filename
        media_type: MIME type

    Returns:
        (storage_path, error) — storage_path on success, error message on failure
    """
    try:
        # Ensure recordings directory exists
        session_dir = os.path.join(RECORDINGS_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)

        # Sanitise filename
        safe_name = f"{session_id}_{filename}"
        storage_path = os.path.join(session_dir, safe_name)

        # Write file
        if isinstance(file_data, bytes):
            with open(storage_path, 'wb') as f:
                f.write(file_data)
            size_bytes = len(file_data)
        else:
            file_data.save(storage_path)
            size_bytes = os.path.getsize(storage_path)

        # Check size limit
        if size_bytes > MAX_RECORDING_SIZE_MB * 1024 * 1024:
            os.remove(storage_path)
            return None, f'Recording exceeds {MAX_RECORDING_SIZE_MB}MB limit'

        # Record metadata in DB
        add_recording_metadata(session_id, safe_name, size_bytes, media_type, storage_path)

        logger.info("Saved recording %s (%d bytes) for session %s", safe_name, size_bytes, session_id)
        return storage_path, None

    except Exception as e:
        logger.error("Failed to save recording for session %s: %s", session_id, e)
        return None, str(e)


def get_recording_path(session_id: str, recording_index: int = 0) -> Optional[str]:
    """
    Get the filesystem path of a recording for download.
    Returns None if session or recording not found.
    """
    session = get_session_by_id(session_id)
    if not session:
        return None
    recordings = session.get('recordings', [])
    if recording_index >= len(recordings):
        return None
    rec = recordings[recording_index]
    path = rec.get('storage_path', '')
    if path and os.path.exists(path):
        return path
    return None


# ─── Live Interview Helpers ─────────────────────────────────────────────────────

def interviewer_join_session(session_id: str) -> Optional[Dict]:
    """Mark the interviewer as having joined the live interview session."""
    return _update_session(session_id, {'interviewer_joined': True})


def candidate_join_session(session_id: str) -> Optional[Dict]:
    """Mark the candidate as having joined the live interview session."""
    return _update_session(session_id, {'candidate_joined': True})


def update_interviewer_controls(
    session_id: str,
    candidate_camera_on: Optional[bool] = None,
    candidate_mic_on: Optional[bool] = None,
) -> Optional[Dict]:
    """
    Interviewer-only control: toggle candidate's camera/mic state.
    The frontend reads these flags and enforces them on the candidate side.
    """
    update: Dict = {}
    if candidate_camera_on is not None:
        update['candidate_camera_on'] = candidate_camera_on
    if candidate_mic_on is not None:
        update['candidate_mic_on'] = candidate_mic_on
    if not update:
        return get_session_by_id(session_id)
    return _update_session(session_id, update)


# ─── Cleanup / Expiry ──────────────────────────────────────────────────────────

def expire_stale_sessions() -> int:
    """
    Mark all 'scheduled' or 'waiting' sessions whose expires_at has passed as 'expired'.
    Intended to be called periodically (e.g. every hour via a background worker).
    Returns the number of sessions expired.
    """
    db = get_db()
    now = datetime.utcnow()
    result = db['video_interviews'].update_many(
        {
            'status': {'$in': ['scheduled', 'waiting']},
            'expires_at': {'$lt': now},
        },
        {'$set': {'status': 'expired', 'updated_at': now}},
    )
    if result.modified_count:
        logger.info("Expired %d stale video interview sessions.", result.modified_count)
    return result.modified_count
