"""
Tests for Video Interview System (Phase 3)
==========================================
Unit tests for video_interview_service.py and video_interview_routes.py
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime, timedelta
from bson import ObjectId

# ── Ensure project root on sys.path ──────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# ═══════════════════════════════════════════════════════════════════════════════
# Section 1: Service-layer unit tests (no Flask, mock DB)
# ═══════════════════════════════════════════════════════════════════════════════

class TestTokenGeneration:
    """Test meeting token / link helpers."""

    def test_generate_meeting_token_length(self):
        from backend.services.video_interview_service import generate_meeting_token
        token = generate_meeting_token()
        # token_urlsafe(32) produces a 43-char string
        assert isinstance(token, str)
        assert len(token) >= 40  # at least 40 chars (base64 encoding of 32 bytes)

    def test_generate_meeting_token_uniqueness(self):
        from backend.services.video_interview_service import generate_meeting_token
        tokens = {generate_meeting_token() for _ in range(50)}
        assert len(tokens) == 50, "Tokens should be unique"

    def test_generate_meeting_link(self):
        from backend.services.video_interview_service import generate_meeting_link
        link = generate_meeting_link('http://localhost:5000', 'abc123token')
        assert link == 'http://localhost:5000/interview/room/abc123token'

    def test_generate_meeting_link_strips_trailing_slash(self):
        from backend.services.video_interview_service import generate_meeting_link
        link = generate_meeting_link('http://example.com/', 'tok')
        assert link == 'http://example.com/interview/room/tok'


class TestSessionConstants:
    """Verify module-level constants."""

    def test_session_statuses(self):
        from backend.services.video_interview_service import SESSION_STATUSES
        assert 'scheduled' in SESSION_STATUSES
        assert 'in_progress' in SESSION_STATUSES
        assert 'completed' in SESSION_STATUSES
        assert 'expired' in SESSION_STATUSES
        assert 'cancelled' in SESSION_STATUSES

    def test_supported_media_types(self):
        from backend.services.video_interview_service import SUPPORTED_MEDIA_TYPES
        assert 'video/webm' in SUPPORTED_MEDIA_TYPES
        assert 'audio/webm' in SUPPORTED_MEDIA_TYPES


class TestCreateInterviewSession:
    """Test create_interview_session with mocked DB."""

    @patch('backend.services.video_interview_service.get_db')
    def test_create_session_returns_doc(self, mock_get_db):
        from backend.services.video_interview_service import create_interview_session

        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.inserted_id = ObjectId()
        mock_collection.insert_one.return_value = mock_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_get_db.return_value = mock_db

        job_id = str(ObjectId())
        candidate_id = str(ObjectId())
        scheduler_id = str(ObjectId())

        doc = create_interview_session(
            job_id=job_id,
            candidate_id=candidate_id,
            scheduled_by=scheduler_id,
            interview_type='ai_automated',
            duration_minutes=45,
            expiry_hours=24,
            base_url='http://test.com',
        )

        assert doc is not None
        assert doc['status'] == 'scheduled'
        assert doc['interview_type'] == 'ai_automated'
        assert doc['duration_minutes'] == 45
        assert '/interview/room/' in doc['meeting_link']
        assert doc['token'] is not None
        assert doc['webcam_detected'] is False
        assert doc['audio_detected'] is False
        assert doc['expires_at'] > doc['scheduled_at']
        mock_collection.insert_one.assert_called_once()

    @patch('backend.services.video_interview_service.get_db')
    def test_create_session_with_questions(self, mock_get_db):
        from backend.services.video_interview_service import create_interview_session

        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.inserted_id = ObjectId()
        mock_collection.insert_one.return_value = mock_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_get_db.return_value = mock_db

        questions = [{'question': 'Tell me about yourself', 'type': 'behavioral'}]
        doc = create_interview_session(
            job_id=str(ObjectId()),
            candidate_id=str(ObjectId()),
            scheduled_by=str(ObjectId()),
            questions=questions,
        )
        assert doc['questions'] == questions


class TestJoinSession:
    """Test join_session logic."""

    @patch('backend.services.video_interview_service.get_db')
    @patch('backend.services.video_interview_service.get_session_by_token')
    def test_join_session_not_found(self, mock_get_token, mock_db):
        from backend.services.video_interview_service import join_session
        mock_get_token.return_value = None
        session, error = join_session('nonexistent')
        assert session is None
        assert 'not found' in error.lower()

    @patch('backend.services.video_interview_service._update_session')
    @patch('backend.services.video_interview_service.get_session_by_token')
    def test_join_session_cancelled(self, mock_get_token, mock_update):
        from backend.services.video_interview_service import join_session
        mock_get_token.return_value = {'status': 'cancelled', '_id': ObjectId()}
        session, error = join_session('tok')
        assert session is None
        assert 'cancelled' in error.lower()

    @patch('backend.services.video_interview_service._update_session')
    @patch('backend.services.video_interview_service.get_session_by_token')
    def test_join_session_completed(self, mock_get_token, mock_update):
        from backend.services.video_interview_service import join_session
        mock_get_token.return_value = {'status': 'completed', '_id': ObjectId()}
        session, error = join_session('tok')
        assert session is None
        assert 'completed' in error.lower()

    @patch('backend.services.video_interview_service._update_session')
    @patch('backend.services.video_interview_service.get_session_by_token')
    def test_join_session_expired(self, mock_get_token, mock_update):
        from backend.services.video_interview_service import join_session
        sid = ObjectId()
        mock_get_token.return_value = {
            'status': 'scheduled',
            '_id': sid,
            'expires_at': datetime.utcnow() - timedelta(hours=1),
        }
        mock_update.return_value = {'status': 'expired'}
        session, error = join_session('tok')
        assert session is None
        assert 'expired' in error.lower()

    @patch('backend.services.video_interview_service._update_session')
    @patch('backend.services.video_interview_service.get_session_by_token')
    def test_join_session_success(self, mock_get_token, mock_update):
        from backend.services.video_interview_service import join_session
        sid = ObjectId()
        original = {
            'status': 'scheduled',
            '_id': sid,
            'expires_at': datetime.utcnow() + timedelta(hours=24),
        }
        updated = dict(original)
        updated['status'] = 'waiting'
        mock_get_token.return_value = original
        mock_update.return_value = updated

        session, error = join_session('tok')
        assert error is None
        assert session['status'] == 'waiting'


class TestStateTransitions:
    """Test start/pause/resume/complete/cancel."""

    @patch('backend.services.video_interview_service._update_session')
    def test_start_interview(self, mock_update):
        from backend.services.video_interview_service import start_interview
        mock_update.return_value = {'status': 'in_progress'}
        result = start_interview('abc')
        assert result['status'] == 'in_progress'

    @patch('backend.services.video_interview_service._update_session')
    def test_pause_interview(self, mock_update):
        from backend.services.video_interview_service import pause_interview
        mock_update.return_value = {'status': 'paused'}
        result = pause_interview('abc')
        assert result['status'] == 'paused'

    @patch('backend.services.video_interview_service._update_session')
    def test_resume_interview(self, mock_update):
        from backend.services.video_interview_service import resume_interview
        mock_update.return_value = {'status': 'in_progress'}
        result = resume_interview('abc')
        assert result['status'] == 'in_progress'

    @patch('backend.services.video_interview_service._update_session')
    def test_complete_interview(self, mock_update):
        from backend.services.video_interview_service import complete_interview
        mock_update.return_value = {'status': 'completed', 'overall_score': 85.5}
        result = complete_interview('abc', overall_score=85.5)
        assert result['status'] == 'completed'
        assert result['overall_score'] == 85.5

    @patch('backend.services.video_interview_service._update_session')
    def test_cancel_interview(self, mock_update):
        from backend.services.video_interview_service import cancel_interview
        mock_update.return_value = {'status': 'cancelled', 'cancel_reason': 'Rescheduled'}
        result = cancel_interview('abc', reason='Rescheduled')
        assert result['status'] == 'cancelled'


class TestMediaStatus:
    """Test webcam / audio status updates."""

    @patch('backend.services.video_interview_service._update_session')
    def test_update_webcam_detected(self, mock_update):
        from backend.services.video_interview_service import update_media_status
        mock_update.return_value = {'webcam_detected': True, 'audio_detected': False}
        result = update_media_status('abc', webcam_detected=True)
        assert result['webcam_detected'] is True

    @patch('backend.services.video_interview_service.get_session_by_id')
    def test_update_no_changes(self, mock_get):
        from backend.services.video_interview_service import update_media_status
        mock_get.return_value = {'webcam_detected': False}
        result = update_media_status('abc')
        assert result is not None  # returns existing session


class TestSubmitAnswer:
    """Test answer submission."""

    @patch('backend.services.video_interview_service.get_db')
    def test_submit_answer_success(self, mock_get_db):
        from backend.services.video_interview_service import submit_answer

        mock_db = MagicMock()
        mock_collection = MagicMock()
        updated_doc = {'current_question_index': 1, 'answers': [{'question_index': 0}]}
        mock_collection.find_one_and_update.return_value = updated_doc
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_get_db.return_value = mock_db

        result = submit_answer(str(ObjectId()), 0, 'My answer text', {'score': 8})
        assert result['current_question_index'] == 1
        mock_collection.find_one_and_update.assert_called_once()


class TestRecordingMetadata:
    """Test recording metadata storage."""

    @patch('backend.services.video_interview_service.get_db')
    def test_add_recording_metadata(self, mock_get_db):
        from backend.services.video_interview_service import add_recording_metadata

        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.find_one_and_update.return_value = {
            'recordings': [{'filename': 'test.webm'}]
        }
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_get_db.return_value = mock_db

        result = add_recording_metadata(str(ObjectId()), 'test.webm', 1000, 'video/webm')
        assert len(result['recordings']) == 1


class TestAIIntegration:
    """Test AI question generation and evaluation."""

    @patch('backend.services.video_interview_service._update_session')
    @patch('backend.services.ai_interviewer_service_v2.create_interview_schedule_advanced')
    @patch('backend.services.ai_interviewer_service_v2.generate_dynamic_interview_questions')
    def test_generate_questions_for_session(self, mock_gen, mock_sched, mock_update):
        from backend.services.video_interview_service import generate_questions_for_session

        mock_gen.return_value = [
            {'question': 'What is OOP?', 'type': 'technical'},
            {'question': 'Tell me about teamwork', 'type': 'behavioral'},
        ]
        mock_sched.return_value = {'schedule': []}
        mock_update.return_value = {'questions': mock_gen.return_value, 'schedule': mock_sched.return_value}

        result = generate_questions_for_session('abc', job={'title': 'Developer'})
        assert len(result['questions']) == 2

    @patch('backend.services.video_interview_service._update_session')
    @patch('backend.services.video_interview_service.get_session_by_id')
    @patch('backend.services.ai_interviewer_service_v2.evaluate_answer_advanced')
    def test_evaluate_session_answers(self, mock_eval, mock_get, mock_update):
        from backend.services.video_interview_service import evaluate_session_answers

        mock_get.return_value = {
            'questions': [{'question': 'Q1', 'expected_keywords': ['python']}],
            'answers': [{'question_index': 0, 'answer_text': 'I know python well'}],
        }
        mock_eval.return_value = {
            'score': 7, 'max_score': 10, 'percentage': 70,
            'feedback': 'Good', 'strengths': ['Python'], 'improvements': [],
        }
        mock_update.return_value = {'overall_score': 70.0}

        result = evaluate_session_answers('abc')
        assert result['overall_score'] == 70.0


class TestEmailInvitation:
    """Test email invitation helper."""

    @patch('backend.utils.email_service.EmailService')
    def test_send_interview_invitation_success(self, MockEmailService):
        from backend.services.video_interview_service import send_interview_invitation

        mock_instance = MagicMock()
        mock_instance.send_email.return_value = True
        MockEmailService.return_value = mock_instance

        result = send_interview_invitation(
            candidate_email='test@example.com',
            candidate_name='Alice',
            job_title='Developer',
            company_name='Acme',
            meeting_link='http://test.com/interview/room/token123',
        )
        assert result is True
        mock_instance.send_email.assert_called_once()

    @patch('backend.utils.email_service.EmailService', side_effect=Exception('SMTP down'))
    def test_send_invitation_failure(self, MockEmailService):
        from backend.services.video_interview_service import send_interview_invitation
        result = send_interview_invitation(
            candidate_email='bad@example.com',
            candidate_name='Bob',
            job_title='Tester',
            company_name='Corp',
            meeting_link='http://test.com/interview/room/xxx',
        )
        assert result is False


class TestWebSocketNotification:
    """Test WebSocket notification helper."""

    @patch('backend.services.websocket_service.get_websocket_manager')
    def test_notify_interview_scheduled_ws(self, mock_get_ws):
        from backend.services.video_interview_service import notify_interview_scheduled_ws

        mock_ws = MagicMock()
        mock_ws.notify_interview_scheduled.return_value = True
        mock_get_ws.return_value = mock_ws

        session_doc = {
            '_id': ObjectId(),
            'meeting_link': 'http://test.com/interview/room/tok',
            'job_id': ObjectId(),
            'status': 'scheduled',
            'expires_at': datetime.utcnow() + timedelta(hours=48),
            'duration_minutes': 60,
        }
        result = notify_interview_scheduled_ws('user123', session_doc)
        assert result is True

    @patch('backend.services.websocket_service.get_websocket_manager')
    def test_notify_ws_no_manager(self, mock_get_ws):
        from backend.services.video_interview_service import notify_interview_scheduled_ws
        mock_get_ws.return_value = None
        result = notify_interview_scheduled_ws('user123', {'_id': ObjectId()})
        assert result is False


class TestExpireStale:
    """Test session expiry cleanup."""

    @patch('backend.services.video_interview_service.get_db')
    def test_expire_stale_sessions(self, mock_get_db):
        from backend.services.video_interview_service import expire_stale_sessions

        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.modified_count = 3
        mock_collection.update_many.return_value = mock_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_get_db.return_value = mock_db

        count = expire_stale_sessions()
        assert count == 3


# ═══════════════════════════════════════════════════════════════════════════════
# Section 2: Route-layer tests (Flask test client)
# ═══════════════════════════════════════════════════════════════════════════════

class TestVideoInterviewRoutes:
    """Test route endpoints with Flask test client."""

    @pytest.fixture(autouse=True)
    def setup_app(self):
        """Create a test Flask app with the video interview blueprint."""
        from flask import Flask
        from flask_jwt_extended import JWTManager
        from backend.routes.video_interview_routes import bp

        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['JWT_SECRET_KEY'] = 'test-secret'
        JWTManager(self.app)
        self.app.register_blueprint(bp, url_prefix='/api/video-interview')
        self.client = self.app.test_client()

    @patch('backend.routes.video_interview_routes.get_db')
    @patch('backend.routes.video_interview_routes.join_session')
    def test_get_session_public_success(self, mock_join, mock_db):
        """GET /session/<token> should return session without JWT."""
        mock_join.return_value = (
            {
                '_id': ObjectId(),
                'status': 'waiting',
                'token': 'secret-token',
                'questions': [],
                'meeting_link': 'http://test.com/interview/room/abc',
            },
            None,
        )
        resp = self.client.get('/api/video-interview/session/abc-token')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'session' in data
        # Token should be stripped for security
        assert 'token' not in data['session']

    @patch('backend.routes.video_interview_routes.join_session')
    def test_get_session_not_found(self, mock_join):
        mock_join.return_value = (None, 'Interview session not found.')
        resp = self.client.get('/api/video-interview/session/bad-token')
        assert resp.status_code == 400

    @patch('backend.routes.video_interview_routes.start_interview')
    def test_start_interview_route(self, mock_start):
        mock_start.return_value = {'_id': ObjectId(), 'status': 'in_progress'}
        resp = self.client.post(
            '/api/video-interview/start',
            json={'session_id': str(ObjectId())},
        )
        assert resp.status_code == 200
        assert resp.get_json()['message'] == 'Interview started'

    @patch('backend.routes.video_interview_routes.start_interview')
    def test_start_missing_session_id(self, mock_start):
        resp = self.client.post('/api/video-interview/start', json={})
        assert resp.status_code == 400

    @patch('backend.routes.video_interview_routes.update_media_status')
    def test_webcam_status_update(self, mock_update):
        mock_update.return_value = {'webcam_detected': True, 'audio_detected': True}
        resp = self.client.post(
            '/api/video-interview/webcam-status',
            json={'session_id': str(ObjectId()), 'webcam_detected': True, 'audio_detected': True},
        )
        assert resp.status_code == 200

    @patch('backend.routes.video_interview_routes.get_session_by_id')
    @patch('backend.routes.video_interview_routes.submit_answer')
    def test_submit_answer_route(self, mock_submit, mock_get):
        mock_get.return_value = {
            'questions': [{'question': 'Q1', 'expected_keywords': ['test']}],
        }
        mock_submit.return_value = {'current_question_index': 1}
        resp = self.client.post(
            '/api/video-interview/submit-answer',
            json={
                'session_id': str(ObjectId()),
                'question_index': 0,
                'answer_text': 'My test answer',
                'evaluate': False,
            },
        )
        assert resp.status_code == 200

    @patch('backend.routes.video_interview_routes.submit_answer')
    def test_submit_answer_empty_text(self, mock_submit):
        resp = self.client.post(
            '/api/video-interview/submit-answer',
            json={'session_id': str(ObjectId()), 'question_index': 0, 'answer_text': '   '},
        )
        assert resp.status_code == 400

    @patch('backend.routes.video_interview_routes.add_recording_metadata')
    def test_upload_recording_route(self, mock_add):
        mock_add.return_value = {'recordings': [{'filename': 'rec.webm'}]}
        resp = self.client.post(
            '/api/video-interview/upload-recording',
            json={
                'session_id': str(ObjectId()),
                'filename': 'rec.webm',
                'size_bytes': 5000,
                'media_type': 'video/webm',
            },
        )
        assert resp.status_code == 200

    @patch('backend.routes.video_interview_routes.pause_interview')
    def test_pause_route(self, mock_pause):
        mock_pause.return_value = {'status': 'paused'}
        resp = self.client.post(
            '/api/video-interview/pause',
            json={'session_id': str(ObjectId())},
        )
        assert resp.status_code == 200

    @patch('backend.routes.video_interview_routes.resume_interview')
    def test_resume_route(self, mock_resume):
        mock_resume.return_value = {'status': 'in_progress'}
        resp = self.client.post(
            '/api/video-interview/resume',
            json={'session_id': str(ObjectId())},
        )
        assert resp.status_code == 200

    @patch('backend.routes.video_interview_routes.evaluate_session_answers')
    @patch('backend.routes.video_interview_routes.complete_interview')
    def test_complete_route(self, mock_complete, mock_eval):
        mock_eval.return_value = {'overall_score': 80}
        mock_complete.return_value = {'_id': ObjectId(), 'status': 'completed', 'overall_score': 80}
        resp = self.client.post(
            '/api/video-interview/complete',
            json={'session_id': str(ObjectId()), 'auto_evaluate': True},
        )
        assert resp.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])


# ═══════════════════════════════════════════════════════════════════════════════
# Section 3: Timezone, Malpractice, Interviewer Controls, 25-Question tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestTimezoneHelpers:
    """Test timezone conversion utilities."""

    def test_timezone_offsets_dict_exists(self):
        from backend.services.video_interview_service import TIMEZONE_OFFSETS
        assert isinstance(TIMEZONE_OFFSETS, dict)
        assert 'IST' in TIMEZONE_OFFSETS
        assert 'UTC' in TIMEZONE_OFFSETS
        assert 'PST' in TIMEZONE_OFFSETS
        assert 'EST' in TIMEZONE_OFFSETS

    def test_ist_offset_is_5_5(self):
        from backend.services.video_interview_service import TIMEZONE_OFFSETS
        assert TIMEZONE_OFFSETS['IST'] == 5.5

    def test_utc_offset_is_zero(self):
        from backend.services.video_interview_service import TIMEZONE_OFFSETS
        assert TIMEZONE_OFFSETS['UTC'] == 0

    def test_convert_utc_to_timezone_ist(self):
        from backend.services.video_interview_service import convert_utc_to_timezone
        utc_dt = datetime(2024, 6, 15, 10, 0, 0)  # 10:00 UTC
        local_dt, display_str = convert_utc_to_timezone(utc_dt, 'IST')
        # IST = UTC+5:30 → 15:30 IST
        assert local_dt.hour == 15
        assert local_dt.minute == 30
        assert 'IST' in display_str

    def test_convert_utc_to_timezone_pst(self):
        from backend.services.video_interview_service import convert_utc_to_timezone
        utc_dt = datetime(2024, 6, 15, 20, 0, 0)  # 20:00 UTC
        local_dt, display_str = convert_utc_to_timezone(utc_dt, 'PST')
        # PST = UTC-8 → 12:00 PST
        assert local_dt.hour == 12
        assert 'PST' in display_str

    def test_convert_utc_to_timezone_case_insensitive(self):
        from backend.services.video_interview_service import convert_utc_to_timezone
        utc_dt = datetime(2024, 1, 1, 12, 0, 0)
        local_dt, display = convert_utc_to_timezone(utc_dt, 'ist')
        assert local_dt.hour == 17
        assert local_dt.minute == 30

    def test_convert_timezone_to_utc_ist(self):
        from backend.services.video_interview_service import convert_timezone_to_utc
        local_dt = datetime(2024, 6, 15, 15, 30, 0)  # 15:30 IST
        utc_dt = convert_timezone_to_utc(local_dt, 'IST')
        # IST = UTC+5:30 → 10:00 UTC
        assert utc_dt.hour == 10
        assert utc_dt.minute == 0

    def test_convert_timezone_to_utc_unknown_defaults_zero(self):
        from backend.services.video_interview_service import convert_timezone_to_utc
        local_dt = datetime(2024, 1, 1, 12, 0, 0)
        utc_dt = convert_timezone_to_utc(local_dt, 'UNKNOWN')
        assert utc_dt == local_dt  # offset 0 → no change

    def test_roundtrip_conversion(self):
        from backend.services.video_interview_service import convert_utc_to_timezone, convert_timezone_to_utc
        original_utc = datetime(2024, 3, 20, 8, 45, 0)
        local_dt, _ = convert_utc_to_timezone(original_utc, 'JST')
        back_to_utc = convert_timezone_to_utc(local_dt, 'JST')
        assert back_to_utc == original_utc


class TestMalpracticeLogging:
    """Test anti-malpractice event logging."""

    @patch('backend.services.video_interview_service.get_db')
    def test_log_malpractice_event_tab_switch(self, mock_get_db):
        from backend.services.video_interview_service import log_malpractice_event

        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.find_one_and_update.return_value = {
            'malpractice_score': 3,
            'malpractice_events': [{'event_type': 'tab_switch'}],
        }
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_get_db.return_value = mock_db

        result = log_malpractice_event(str(ObjectId()), 'tab_switch')
        assert result is not None
        assert result['malpractice_score'] == 3
        mock_collection.find_one_and_update.assert_called_once()

    @patch('backend.services.video_interview_service.get_db')
    def test_log_malpractice_event_with_details(self, mock_get_db):
        from backend.services.video_interview_service import log_malpractice_event

        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.find_one_and_update.return_value = {
            'malpractice_score': 5,
            'malpractice_events': [{'event_type': 'multiple_screens'}],
        }
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_get_db.return_value = mock_db

        result = log_malpractice_event(
            str(ObjectId()), 'multiple_screens', details={'screens': 2}
        )
        assert result['malpractice_score'] == 5

    @patch('backend.services.video_interview_service.get_db')
    def test_log_malpractice_event_not_found(self, mock_get_db):
        from backend.services.video_interview_service import log_malpractice_event

        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.find_one_and_update.return_value = None
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_get_db.return_value = mock_db

        result = log_malpractice_event(str(ObjectId()), 'tab_switch')
        assert result is None


class TestInterviewerControls:
    """Test interviewer camera/mic control functions."""

    @patch('backend.services.video_interview_service._update_session')
    def test_update_controls_camera_off(self, mock_update):
        from backend.services.video_interview_service import update_interviewer_controls
        mock_update.return_value = {'candidate_camera_on': False}
        result = update_interviewer_controls(str(ObjectId()), candidate_camera_on=False)
        assert result['candidate_camera_on'] is False

    @patch('backend.services.video_interview_service._update_session')
    def test_update_controls_mic_off(self, mock_update):
        from backend.services.video_interview_service import update_interviewer_controls
        mock_update.return_value = {'candidate_mic_on': False}
        result = update_interviewer_controls(str(ObjectId()), candidate_mic_on=False)
        assert result['candidate_mic_on'] is False

    @patch('backend.services.video_interview_service._update_session')
    def test_update_controls_both(self, mock_update):
        from backend.services.video_interview_service import update_interviewer_controls
        mock_update.return_value = {'candidate_camera_on': True, 'candidate_mic_on': True}
        result = update_interviewer_controls(str(ObjectId()), candidate_camera_on=True, candidate_mic_on=True)
        assert result['candidate_camera_on'] is True
        assert result['candidate_mic_on'] is True

    @patch('backend.services.video_interview_service.get_session_by_id')
    def test_update_controls_no_changes(self, mock_get):
        from backend.services.video_interview_service import update_interviewer_controls
        mock_get.return_value = {'candidate_camera_on': True}
        result = update_interviewer_controls(str(ObjectId()))
        assert result is not None  # returns existing session


class TestQuestionGeneration25:
    """Test that 25 questions can be generated."""

    def test_generate_25_questions(self):
        from backend.services.ai_interviewer_service_v2 import generate_dynamic_interview_questions
        questions = generate_dynamic_interview_questions(
            job={'title': 'Software Developer', 'required_skills': ['Python', 'Flask', 'MongoDB'], 'experience_level': 'mid'},
            num_questions=25,
        )
        assert len(questions) >= 20, f"Expected at least 20 questions, got {len(questions)}"

    def test_generate_default_questions_count(self):
        from backend.services.ai_interviewer_service_v2 import generate_dynamic_interview_questions
        questions = generate_dynamic_interview_questions(
            job={'title': 'Data Analyst', 'required_skills': ['SQL', 'Python']},
        )
        assert len(questions) >= 5


class TestCreateSessionWithTimezone:
    """Test create_interview_session with timezone and interviewer fields."""

    @patch('backend.services.video_interview_service.get_db')
    def test_create_session_with_timezone(self, mock_get_db):
        from backend.services.video_interview_service import create_interview_session

        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_result = MagicMock()
        mock_result.inserted_id = ObjectId()
        mock_collection.insert_one.return_value = mock_result
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_get_db.return_value = mock_db

        doc = create_interview_session(
            job_id=str(ObjectId()),
            candidate_id=str(ObjectId()),
            scheduled_by=str(ObjectId()),
            candidate_timezone='IST',
            scheduled_time_utc=datetime(2024, 6, 15, 10, 0, 0),
        )
        assert doc is not None
        assert doc.get('candidate_timezone') == 'IST'
        assert doc.get('scheduled_time_utc') == datetime(2024, 6, 15, 10, 0, 0)


# ═══════════════════════════════════════════════════════════════════════════════
# Section 4: Route tests for new endpoints
# ═══════════════════════════════════════════════════════════════════════════════

class TestMalpracticeRoute:
    """Test malpractice-event route."""

    @pytest.fixture(autouse=True)
    def setup_app(self):
        from flask import Flask
        from flask_jwt_extended import JWTManager
        from backend.routes.video_interview_routes import bp

        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['JWT_SECRET_KEY'] = 'test-secret'
        JWTManager(self.app)
        self.app.register_blueprint(bp, url_prefix='/api/video-interview')
        self.client = self.app.test_client()

    @patch('backend.routes.video_interview_routes.log_malpractice_event')
    def test_malpractice_event_success(self, mock_log):
        mock_log.return_value = {
            'malpractice_score': 3,
            'malpractice_events': [{'event_type': 'tab_switch'}],
        }
        resp = self.client.post(
            '/api/video-interview/malpractice-event',
            json={'session_id': str(ObjectId()), 'event_type': 'tab_switch'},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['malpractice_score'] == 3

    @patch('backend.routes.video_interview_routes.log_malpractice_event')
    def test_malpractice_event_missing_fields(self, mock_log):
        resp = self.client.post(
            '/api/video-interview/malpractice-event',
            json={'session_id': str(ObjectId())},  # missing event_type
        )
        assert resp.status_code == 400

    @patch('backend.routes.video_interview_routes.log_malpractice_event')
    def test_malpractice_event_invalid_type(self, mock_log):
        resp = self.client.post(
            '/api/video-interview/malpractice-event',
            json={'session_id': str(ObjectId()), 'event_type': 'invalid_event'},
        )
        assert resp.status_code == 400

    @patch('backend.routes.video_interview_routes.log_malpractice_event')
    def test_malpractice_event_session_not_found(self, mock_log):
        mock_log.return_value = None
        resp = self.client.post(
            '/api/video-interview/malpractice-event',
            json={'session_id': str(ObjectId()), 'event_type': 'tab_switch'},
        )
        assert resp.status_code == 404
