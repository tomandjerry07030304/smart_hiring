def test_questions_requires_auth(client):
    """Unauthenticated requests should be rejected by JWT-protected endpoints"""
    resp = client.get('/api/assessments/questions')
    assert resp.status_code in (401, 422)


def test_get_quizzes_requires_auth(client):
    resp = client.get('/api/assessments/quizzes')
    assert resp.status_code in (401, 422)


def test_start_quiz_requires_auth(client):
    resp = client.post('/api/assessments/quizzes/123/start', json={})
    assert resp.status_code in (401, 422)
