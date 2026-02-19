"""
Video Interview Routes
======================
REST API endpoints for the video interview system.

Blueprint prefix (registered in app.py): /api/video-interview

Endpoints
---------
POST /schedule                      Schedule a new video interview
GET  /session/<token>               Join / view a session via meeting link
POST /start                         Start the interview (waiting → in_progress)
POST /pause                         Pause the interview
POST /resume                        Resume a paused interview
POST /complete                      Mark interview as completed
POST /cancel                        Cancel a scheduled interview
POST /submit-answer                 Submit an answer for a question
POST /webcam-status                 Update webcam / audio detection flags
POST /upload-recording              Store recording metadata
POST /upload-recording-file         Upload actual recording file (multipart)
POST /generate-questions            Generate AI questions for a session
POST /evaluate                      Run AI evaluation on all answers
GET  /candidate/<candidate_id>      List sessions for a candidate
GET  /job/<job_id>                  List sessions for a job
GET  /details/<session_id>          Get full session details by ID
POST /malpractice-event             Log an anti-malpractice event
GET  /download-recording/<sid>      Download interview recording
POST /interviewer-join              Interviewer joins live session
POST /interviewer-controls          Toggle candidate camera/mic
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId

from backend.models.database import get_db
from backend.security.rbac import require_permission, Permissions
from backend.services.video_interview_service import (
    create_interview_session,
    get_session_by_token,
    get_session_by_id,
    get_sessions_for_candidate,
    get_sessions_for_job,
    join_session,
    start_interview,
    pause_interview,
    resume_interview,
    complete_interview,
    cancel_interview,
    update_media_status,
    submit_answer,
    add_recording_metadata,
    generate_questions_for_session,
    evaluate_session_answers,
    send_interview_invitation,
    notify_interview_scheduled_ws,
    log_malpractice_event,
    save_recording_file,
    get_recording_path,
    interviewer_join_session,
    candidate_join_session,
    update_interviewer_controls,
    convert_utc_to_timezone,
    convert_timezone_to_utc,
)

bp = Blueprint('video_interview', __name__)

import logging
logger = logging.getLogger(__name__)


# ─── Helpers ────────────────────────────────────────────────────────────────────

def _get_user_info(current_user):
    """Extract user_id and role from JWT identity (same pattern as ai_interview_routes)."""
    if isinstance(current_user, str):
        user_id = current_user
        db = get_db()
        user = db['users'].find_one({'_id': ObjectId(user_id)})
        return user_id, user.get('role') if user else None
    return current_user.get('user_id'), current_user.get('role')


def _serialise(doc):
    """Make a Mongo document JSON-serialisable (ObjectId → str, datetime → ISO)."""
    if doc is None:
        return None
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, list):
            out[k] = [_serialise(i) if isinstance(i, dict) else
                       str(i) if isinstance(i, ObjectId) else
                       i.isoformat() if isinstance(i, datetime) else i
                       for i in v]
        elif isinstance(v, dict):
            out[k] = _serialise(v)
        else:
            out[k] = v
    return out


# ─── Schedule Interview ────────────────────────────────────────────────────────

@bp.route('/schedule', methods=['POST'])
@jwt_required()
@require_permission(Permissions.MANAGE_APPLICATIONS)
def schedule_interview():
    """
    Schedule a new video interview.

    POST /api/video-interview/schedule
    Body: {
        "job_id": "...",
        "candidate_id": "...",
        "interview_type": "ai_automated",    // optional, default ai_automated
        "duration_minutes": 90,              // optional
        "send_email": true,                  // optional, default true
        "expiry_hours": 48,                  // optional
        "scheduled_time": "2024-03-15T10:00:00",  // optional, ISO format
        "candidate_timezone": "IST",         // optional, default UTC
        "interviewer_id": "...",             // optional, for live interviews
        "num_questions": 25                  // optional, default 25
    }
    """
    try:
        user_id, role = _get_user_info(get_jwt_identity())
        data = request.get_json(silent=True) or {}

        job_id = data.get('job_id')
        candidate_id = data.get('candidate_id')
        if not job_id or not candidate_id:
            return jsonify({'error': 'job_id and candidate_id are required'}), 400

        db = get_db()

        # Validate job exists
        job = db['jobs'].find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'error': 'Job not found'}), 404

        # Validate candidate exists
        candidate = db['users'].find_one({'_id': ObjectId(candidate_id)})
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404

        # Parse timezone and scheduled time
        candidate_timezone = data.get('candidate_timezone', 'UTC')
        scheduled_time_utc = None
        if data.get('scheduled_time'):
            try:
                local_dt = datetime.fromisoformat(data['scheduled_time'])
                scheduled_time_utc = convert_timezone_to_utc(local_dt, candidate_timezone)
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid scheduled_time format. Use ISO format.'}), 400

        # Build base URL from request
        base_url = request.host_url.rstrip('/')

        session_doc = create_interview_session(
            job_id=job_id,
            candidate_id=candidate_id,
            scheduled_by=user_id,
            interview_type=data.get('interview_type', 'ai_automated'),
            duration_minutes=data.get('duration_minutes', 90),
            expiry_hours=data.get('expiry_hours', 48),
            base_url=base_url,
            scheduled_time_utc=scheduled_time_utc,
            candidate_timezone=candidate_timezone,
            interviewer_id=data.get('interviewer_id'),
        )

        # Optionally generate questions upfront
        if data.get('generate_questions', False):
            candidate_profile = db['candidates'].find_one({'user_id': ObjectId(candidate_id)})
            session_doc = generate_questions_for_session(
                session_id=str(session_doc['_id']),
                job=job,
                candidate=candidate_profile,
                num_questions=data.get('num_questions', 25),
            ) or session_doc

        # Send email invitation (default True)
        if data.get('send_email', True):
            candidate_email = candidate.get('email', '')
            candidate_name = candidate.get('full_name', candidate.get('name', 'Candidate'))
            job_title = job.get('title', 'Position')
            company_name = job.get('company', job.get('company_name', 'Company'))
            send_interview_invitation(
                candidate_email=candidate_email,
                candidate_name=candidate_name,
                job_title=job_title,
                company_name=company_name,
                meeting_link=session_doc.get('meeting_link', ''),
                duration_minutes=session_doc.get('duration_minutes', 90),
                scheduled_time_display=session_doc.get('scheduled_time_display'),
                candidate_timezone=candidate_timezone,
            )

        # WebSocket notification
        notify_interview_scheduled_ws(candidate_id, session_doc)

        return jsonify({
            'message': 'Interview scheduled successfully',
            'session': _serialise(session_doc),
        }), 201

    except Exception as e:
        logger.error("Error scheduling interview: %s", e, exc_info=True)
        return jsonify({'error': 'Failed to schedule interview', 'details': str(e)}), 500


# ─── Join Session (public-ish — token-based) ───────────────────────────────────

@bp.route('/session/<token>', methods=['GET'])
def get_session_public(token):
    """
    Candidate opens the meeting link.
    No JWT required — authentication is via the secret token.

    GET /api/video-interview/session/<token>
    """
    try:
        session, error = join_session(token)
        if error:
            return jsonify({'error': error}), 400

        # Auto-generate questions if none exist
        if not session.get('questions') or len(session.get('questions', [])) == 0:
            try:
                db = get_db()
                job = db['jobs'].find_one({'_id': session.get('job_id')})
                candidate = db['candidates'].find_one({'user_id': session.get('candidate_id')})
                if not candidate:
                    candidate = db['users'].find_one({'_id': session.get('candidate_id')})
                
                if job:
                    updated = generate_questions_for_session(
                        session_id=str(session['_id']),
                        job=job,
                        candidate=candidate,
                        num_questions=10,
                    )
                    if updated:
                        session = updated
                    logger.info("✅ Auto-generated questions for session %s", session['_id'])
            except Exception as qe:
                logger.warning("⚠️ Could not auto-generate questions: %s", qe)

        # Also fetch candidate name and job title for the interview room
        try:
            db = get_db()
            candidate_user = db['users'].find_one({'_id': session.get('candidate_id')})
            job_doc = db['jobs'].find_one({'_id': session.get('job_id')})
            extra = {}
            if candidate_user:
                extra['candidate_name'] = candidate_user.get('full_name', candidate_user.get('name', 'Candidate'))
            if job_doc:
                extra['job_title'] = job_doc.get('title', 'Position')
                extra['company_name'] = job_doc.get('company', job_doc.get('company_name', 'Company'))
        except Exception:
            extra = {}

        # Return safe subset (no internal fields)
        safe = _serialise(session)
        safe.update(extra)
        # Remove token from response for security
        safe.pop('token', None)
        return jsonify({'session': safe}), 200

    except Exception as e:
        logger.error("Error joining session: %s", e)
        return jsonify({'error': 'Failed to load interview session'}), 500


# ─── Start / Pause / Resume / Complete / Cancel ────────────────────────────────

@bp.route('/start', methods=['POST'])
@jwt_required(optional=True)
def start_interview_route():
    """
    Transition session from 'waiting' → 'in_progress'.

    POST /api/video-interview/start
    Body: { "session_id": "..." }
    """
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400

        session = start_interview(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        return jsonify({'message': 'Interview started', 'session': _serialise(session)}), 200

    except Exception as e:
        logger.error("Error starting interview: %s", e)
        return jsonify({'error': 'Failed to start interview'}), 500


@bp.route('/pause', methods=['POST'])
@jwt_required(optional=True)
def pause_interview_route():
    """Pause an in-progress interview."""
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400

        session = pause_interview(session_id)
        return jsonify({'message': 'Interview paused', 'session': _serialise(session)}), 200

    except Exception as e:
        logger.error("Error pausing interview: %s", e)
        return jsonify({'error': 'Failed to pause interview'}), 500


@bp.route('/resume', methods=['POST'])
@jwt_required(optional=True)
def resume_interview_route():
    """Resume a paused interview."""
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400

        session = resume_interview(session_id)
        return jsonify({'message': 'Interview resumed', 'session': _serialise(session)}), 200

    except Exception as e:
        logger.error("Error resuming interview: %s", e)
        return jsonify({'error': 'Failed to resume interview'}), 500


@bp.route('/complete', methods=['POST'])
@jwt_required(optional=True)
def complete_interview_route():
    """
    Mark interview as completed.

    POST /api/video-interview/complete
    Body: { "session_id": "...", "auto_evaluate": true }
    """
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400

        # Optionally run AI evaluation
        if data.get('auto_evaluate', True):
            evaluate_session_answers(session_id)

        session = complete_interview(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        return jsonify({
            'message': 'Interview completed',
            'session': _serialise(session),
        }), 200

    except Exception as e:
        logger.error("Error completing interview: %s", e)
        return jsonify({'error': 'Failed to complete interview'}), 500


@bp.route('/cancel', methods=['POST'])
@jwt_required()
@require_permission(Permissions.MANAGE_APPLICATIONS)
def cancel_interview_route():
    """
    Cancel a scheduled interview.

    POST /api/video-interview/cancel
    Body: { "session_id": "...", "reason": "..." }
    """
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400

        session = cancel_interview(session_id, reason=data.get('reason', ''))
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        return jsonify({'message': 'Interview cancelled', 'session': _serialise(session)}), 200

    except Exception as e:
        logger.error("Error cancelling interview: %s", e)
        return jsonify({'error': 'Failed to cancel interview'}), 500


# ─── Webcam & Audio Status ─────────────────────────────────────────────────────

@bp.route('/webcam-status', methods=['POST'])
@jwt_required(optional=True)
def webcam_status():
    """
    Report webcam / microphone detection status.

    POST /api/video-interview/webcam-status
    Body: {
        "session_id": "...",
        "webcam_detected": true,
        "audio_detected": true
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400

        session = update_media_status(
            session_id,
            webcam_detected=data.get('webcam_detected'),
            audio_detected=data.get('audio_detected'),
        )
        return jsonify({'message': 'Media status updated', 'session': _serialise(session)}), 200

    except Exception as e:
        logger.error("Error updating media status: %s", e)
        return jsonify({'error': 'Failed to update media status'}), 500


# ─── Submit Answer ──────────────────────────────────────────────────────────────

@bp.route('/submit-answer', methods=['POST'])
@jwt_required(optional=True)
def submit_answer_route():
    """
    Submit an answer for a question.

    POST /api/video-interview/submit-answer
    Body: {
        "session_id": "...",
        "question_index": 0,
        "answer_text": "My answer is ..."
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        answer_text = data.get('answer_text', '').strip()
        question_index = data.get('question_index')

        if not session_id or question_index is None:
            return jsonify({'error': 'session_id and question_index are required'}), 400

        if not answer_text:
            return jsonify({'error': 'answer_text cannot be empty'}), 400

        # Optionally evaluate immediately
        evaluation = None
        if data.get('evaluate', True):
            session = get_session_by_id(session_id)
            if session and question_index < len(session.get('questions', [])):
                try:
                    from backend.services.ai_interviewer_service_v2 import evaluate_answer
                    evaluation = evaluate_answer(
                        session['questions'][question_index],
                        answer_text,
                    )
                except Exception as eval_err:
                    logger.warning("Inline evaluation failed: %s", eval_err)

        updated = submit_answer(session_id, question_index, answer_text, evaluation)
        if not updated:
            return jsonify({'error': 'Session not found'}), 404

        return jsonify({
            'message': 'Answer submitted',
            'evaluation': evaluation,
            'current_question_index': updated.get('current_question_index'),
        }), 200

    except Exception as e:
        logger.error("Error submitting answer: %s", e)
        return jsonify({'error': 'Failed to submit answer'}), 500


# ─── Upload Recording Metadata ─────────────────────────────────────────────────

@bp.route('/upload-recording', methods=['POST'])
@jwt_required(optional=True)
def upload_recording():
    """
    Store recording metadata (actual file upload handled separately or via blob).

    POST /api/video-interview/upload-recording
    Body: {
        "session_id": "...",
        "filename": "recording_001.webm",
        "size_bytes": 12345678,
        "media_type": "video/webm",
        "storage_path": "/uploads/recordings/..."
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        filename = data.get('filename')
        if not session_id or not filename:
            return jsonify({'error': 'session_id and filename are required'}), 400

        session = add_recording_metadata(
            session_id=session_id,
            filename=filename,
            size_bytes=data.get('size_bytes', 0),
            media_type=data.get('media_type', 'video/webm'),
            storage_path=data.get('storage_path', ''),
        )
        return jsonify({'message': 'Recording metadata saved', 'session': _serialise(session)}), 200

    except Exception as e:
        logger.error("Error uploading recording: %s", e)
        return jsonify({'error': 'Failed to save recording metadata'}), 500


# ─── Generate AI Questions ──────────────────────────────────────────────────────

@bp.route('/generate-questions', methods=['POST'])
@jwt_required()
@require_permission(Permissions.CREATE_ASSESSMENT)
def generate_questions():
    """
    Generate AI interview questions for an existing session.

    POST /api/video-interview/generate-questions
    Body: {
        "session_id": "...",
        "num_questions": 10
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400

        session = get_session_by_id(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        db = get_db()
        job = db['jobs'].find_one({'_id': session['job_id']})
        if not job:
            return jsonify({'error': 'Associated job not found'}), 404

        candidate = db['candidates'].find_one({'user_id': session['candidate_id']})

        updated = generate_questions_for_session(
            session_id=session_id,
            job=job,
            candidate=candidate,
            num_questions=data.get('num_questions', 10),
        )
        return jsonify({
            'message': 'Questions generated',
            'questions': updated.get('questions', []) if updated else [],
        }), 200

    except Exception as e:
        logger.error("Error generating questions: %s", e)
        return jsonify({'error': 'Failed to generate questions'}), 500


# ─── Evaluate All Answers ──────────────────────────────────────────────────────

@bp.route('/evaluate', methods=['POST'])
@jwt_required()
@require_permission(Permissions.GRADE_ASSESSMENT)
def evaluate_all():
    """
    Run AI evaluation on all answers in a session.

    POST /api/video-interview/evaluate
    Body: { "session_id": "..." }
    """
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400

        result = evaluate_session_answers(session_id)
        if not result:
            return jsonify({'error': 'Session not found or no answers'}), 404

        return jsonify({
            'message': 'Evaluation complete',
            'overall_score': result.get('overall_score'),
            'ai_evaluation': _serialise(result.get('ai_evaluation', {})),
        }), 200

    except Exception as e:
        logger.error("Error evaluating session: %s", e)
        return jsonify({'error': 'Failed to evaluate session'}), 500


# ─── List Sessions ─────────────────────────────────────────────────────────────

@bp.route('/candidate/<candidate_id>', methods=['GET'])
@jwt_required()
def candidate_sessions(candidate_id):
    """List all interview sessions for a candidate."""
    try:
        sessions = get_sessions_for_candidate(candidate_id)
        return jsonify({'sessions': [_serialise(s) for s in sessions]}), 200
    except Exception as e:
        logger.error("Error fetching candidate sessions: %s", e)
        return jsonify({'error': 'Failed to fetch sessions'}), 500


@bp.route('/job/<job_id>', methods=['GET'])
@jwt_required()
@require_permission(Permissions.VIEW_APPLICATIONS)
def job_sessions(job_id):
    """List all interview sessions for a job posting."""
    try:
        sessions = get_sessions_for_job(job_id)
        return jsonify({'sessions': [_serialise(s) for s in sessions]}), 200
    except Exception as e:
        logger.error("Error fetching job sessions: %s", e)
        return jsonify({'error': 'Failed to fetch sessions'}), 500


@bp.route('/details/<session_id>', methods=['GET'])
@jwt_required()
def session_details(session_id):
    """Get full session details by session ID."""
    try:
        session = get_session_by_id(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        return jsonify({'session': _serialise(session)}), 200
    except Exception as e:
        logger.error("Error fetching session details: %s", e)
        return jsonify({'error': 'Failed to fetch session details'}), 500


# ─── Anti-Malpractice Event Logging ────────────────────────────────────────────

@bp.route('/malpractice-event', methods=['POST'])
@jwt_required(optional=True)
def malpractice_event():
    """
    Log an anti-malpractice event detected by the frontend.

    POST /api/video-interview/malpractice-event
    Body: {
        "session_id": "...",
        "event_type": "tab_switch",
        "details": { "tab_away_seconds": 5 }
    }

    Supported event_types:
        tab_switch, face_not_detected, multiple_screens,
        copy_paste, right_click, devtools_open, browser_resize
    """
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        event_type = data.get('event_type')

        if not session_id or not event_type:
            return jsonify({'error': 'session_id and event_type are required'}), 400

        valid_types = [
            'tab_switch', 'face_not_detected', 'multiple_screens',
            'copy_paste', 'right_click', 'devtools_open', 'browser_resize',
        ]
        if event_type not in valid_types:
            return jsonify({'error': f'Invalid event_type. Valid: {valid_types}'}), 400

        session = log_malpractice_event(
            session_id=session_id,
            event_type=event_type,
            details=data.get('details'),
        )
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        return jsonify({
            'message': 'Malpractice event logged',
            'malpractice_score': session.get('malpractice_score', 0),
            'event_count': len(session.get('malpractice_events', [])),
        }), 200

    except Exception as e:
        logger.error("Error logging malpractice event: %s", e)
        return jsonify({'error': 'Failed to log event'}), 500


# ─── Upload Recording File ─────────────────────────────────────────────────────

@bp.route('/upload-recording-file', methods=['POST'])
@jwt_required(optional=True)
def upload_recording_file():
    """
    Upload an actual recording file (multipart/form-data).

    POST /api/video-interview/upload-recording-file
    Form data:
        session_id: "..."
        file: <binary file>
    """
    try:
        session_id = request.form.get('session_id')
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'Empty filename'}), 400

        media_type = file.content_type or 'video/webm'

        storage_path, error = save_recording_file(
            session_id=session_id,
            file_data=file,
            filename=file.filename,
            media_type=media_type,
        )

        if error:
            return jsonify({'error': error}), 400

        return jsonify({
            'message': 'Recording uploaded successfully',
            'storage_path': storage_path,
        }), 200

    except Exception as e:
        logger.error("Error uploading recording file: %s", e)
        return jsonify({'error': 'Failed to upload recording'}), 500


# ─── Download Recording ────────────────────────────────────────────────────────

@bp.route('/download-recording/<session_id>', methods=['GET'])
@jwt_required(optional=True)
def download_recording(session_id):
    """
    Download an interview recording. Available to both candidate and interviewer/recruiter.
    Accepts JWT via Authorization header OR ?token= query parameter.

    GET /api/video-interview/download-recording/<session_id>?index=0
    GET /api/video-interview/download-recording/<session_id>?token=<jwt>
    """
    try:
        from flask_jwt_extended import decode_token
        
        # Try to get identity from header first, then from query param
        identity = get_jwt_identity()
        if not identity:
            token_param = request.args.get('token')
            if token_param:
                try:
                    decoded = decode_token(token_param)
                    identity = decoded.get('sub')
                except Exception:
                    return jsonify({'error': 'Invalid token'}), 401
        
        if not identity:
            return jsonify({'error': 'Authentication required. Pass JWT via Authorization header or ?token= query parameter.'}), 401
        
        if isinstance(identity, dict):
            user_id = identity.get('user_id', str(identity))
            role = identity.get('role', 'candidate')
        else:
            user_id = str(identity)
            db = get_db()
            user = db['users'].find_one({'_id': ObjectId(user_id)})
            role = user.get('role', 'candidate') if user else 'candidate'

        session = get_session_by_id(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        # Authorization: candidate, interviewer, recruiter, or admin
        is_candidate = str(session.get('candidate_id')) == user_id
        is_interviewer = str(session.get('interviewer_id', '')) == user_id
        is_scheduler = str(session.get('scheduled_by', '')) == user_id
        is_admin = role in ('admin', 'super_admin', 'recruiter', 'hr_manager', 'company')

        if not (is_candidate or is_interviewer or is_scheduler or is_admin):
            return jsonify({'error': 'Not authorized to download this recording'}), 403

        recording_index = request.args.get('index', 0, type=int)
        path = get_recording_path(session_id, recording_index)
        if not path:
            return jsonify({'error': 'Recording not found'}), 404

        return send_file(path, as_attachment=True)

    except Exception as e:
        logger.error("Error downloading recording: %s", e)
        return jsonify({'error': 'Failed to download recording'}), 500


# ─── Live Interview — Interviewer Join ──────────────────────────────────────────

@bp.route('/interviewer-join', methods=['POST'])
@jwt_required()
@require_permission(Permissions.VIEW_APPLICATIONS)
def interviewer_join():
    """
    Interviewer joins a live interview session.

    POST /api/video-interview/interviewer-join
    Body: { "session_id": "..." }
    """
    try:
        user_id, role = _get_user_info(get_jwt_identity())
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400

        session = interviewer_join_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        return jsonify({
            'message': 'Interviewer joined',
            'session': _serialise(session),
        }), 200

    except Exception as e:
        logger.error("Error joining as interviewer: %s", e)
        return jsonify({'error': 'Failed to join session'}), 500


# ─── Live Interview — Interviewer Camera/Mic Controls ───────────────────────────

@bp.route('/interviewer-controls', methods=['POST'])
@jwt_required()
@require_permission(Permissions.VIEW_APPLICATIONS)
def interviewer_controls():
    """
    Interviewer controls candidate's camera and microphone.
    Only the interviewer/recruiter can toggle these.

    POST /api/video-interview/interviewer-controls
    Body: {
        "session_id": "...",
        "candidate_camera_on": true,
        "candidate_mic_on": true
    }
    """
    try:
        user_id, role = _get_user_info(get_jwt_identity())
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400

        session = update_interviewer_controls(
            session_id=session_id,
            candidate_camera_on=data.get('candidate_camera_on'),
            candidate_mic_on=data.get('candidate_mic_on'),
        )
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        return jsonify({
            'message': 'Interviewer controls updated',
            'candidate_camera_on': session.get('candidate_camera_on'),
            'candidate_mic_on': session.get('candidate_mic_on'),
        }), 200

    except Exception as e:
        logger.error("Error updating interviewer controls: %s", e)
        return jsonify({'error': 'Failed to update controls'}), 500
