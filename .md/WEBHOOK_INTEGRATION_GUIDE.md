# Webhook Integration Guide

## Overview
Smart Hiring System supports webhooks for real-time event notifications to external systems. Webhooks enable third-party integrations, automated workflows, and custom business logic.

## Supported Events

| Event Type | Description | When Triggered |
|------------|-------------|----------------|
| `application.created` | New job application submitted | When candidate applies to a job |
| `application.status_changed` | Application status updated | When recruiter updates application status |
| `quiz.started` | Assessment started | When candidate begins taking a quiz |
| `quiz.completed` | Assessment completed | When candidate submits quiz answers |
| `job.created` | New job posted | When recruiter creates job posting |
| `job.updated` | Job posting updated | When job details are modified |
| `job.closed` | Job posting closed | When job is no longer accepting applications |
| `candidate.registered` | New candidate account | When candidate completes registration |

## Getting Started

### 1. Create Webhook Subscription

**Endpoint:** `POST /api/webhooks/subscriptions`

```bash
curl -X POST https://my-project-smart-hiring.onrender.com/api/webhooks/subscriptions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-domain.com/webhooks/smart-hiring",
    "events": ["application.created", "quiz.completed"],
    "description": "Production webhook for CRM integration"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "507f1f77bcf86cd799439011",
    "url": "https://your-domain.com/webhooks/smart-hiring",
    "events": ["application.created", "quiz.completed"],
    "active": true,
    "created_at": "2025-01-16T10:00:00Z"
  },
  "message": "Webhook subscription created successfully"
}
```

### 2. Receive Webhook Events

Your endpoint will receive POST requests with the following structure:

**Headers:**
```
Content-Type: application/json
X-Webhook-Signature: sha256=abc123...
X-Webhook-Event: application.created
X-Webhook-Delivery-ID: 507f191e810c19729de860ea
User-Agent: SmartHiring-Webhook/1.0
```

**Payload:**
```json
{
  "event": "application.created",
  "timestamp": "2025-01-16T10:30:00Z",
  "subscription_id": "507f1f77bcf86cd799439011",
  "data": {
    "application_id": "507f191e810c19729de860ea",
    "job_id": "507f1f77bcf86cd799439012",
    "candidate_id": "507f1f77bcf86cd799439013",
    "candidate_name": "John Doe",
    "candidate_email": "john@example.com",
    "job_title": "Senior Software Engineer",
    "applied_at": "2025-01-16T10:30:00Z"
  }
}
```

### 3. Verify Webhook Signature

**Python Example:**
```python
import hmac
import hashlib
import json
from flask import request

def verify_webhook(request, secret):
    """Verify webhook signature"""
    signature = request.headers.get('X-Webhook-Signature')
    
    if not signature or not signature.startswith('sha256='):
        return False
    
    # Get payload
    payload = request.get_json()
    payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
    
    # Calculate expected signature
    expected = hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    expected_signature = f"sha256={expected}"
    
    # Compare signatures
    return hmac.compare_digest(signature, expected_signature)

# Usage
@app.route('/webhooks/smart-hiring', methods=['POST'])
def handle_webhook():
    secret = 'your-webhook-secret'
    
    if not verify_webhook(request, secret):
        return {'error': 'Invalid signature'}, 401
    
    # Process webhook
    event_type = request.headers.get('X-Webhook-Event')
    data = request.get_json()
    
    # Handle event
    if event_type == 'application.created':
        # Create record in CRM
        pass
    
    return {'status': 'received'}, 200
```

**Node.js Example:**
```javascript
const crypto = require('crypto');

function verifyWebhook(req, secret) {
  const signature = req.headers['x-webhook-signature'];
  
  if (!signature || !signature.startsWith('sha256=')) {
    return false;
  }
  
  // Get payload
  const payload = JSON.stringify(req.body);
  
  // Calculate expected signature
  const hmac = crypto.createHmac('sha256', secret);
  hmac.update(payload);
  const expected = `sha256=${hmac.digest('hex')}`;
  
  // Compare signatures
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expected)
  );
}

// Usage
app.post('/webhooks/smart-hiring', (req, res) => {
  const secret = 'your-webhook-secret';
  
  if (!verifyWebhook(req, secret)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }
  
  // Process webhook
  const eventType = req.headers['x-webhook-event'];
  const data = req.body;
  
  // Handle event
  if (eventType === 'application.created') {
    // Create record in CRM
  }
  
  res.json({ status: 'received' });
});
```

## Managing Subscriptions

### List Subscriptions
```bash
GET /api/webhooks/subscriptions
Authorization: Bearer YOUR_JWT_TOKEN
```

### Get Subscription Details
```bash
GET /api/webhooks/subscriptions/{subscription_id}
Authorization: Bearer YOUR_JWT_TOKEN
```

### Update Subscription
```bash
PUT /api/webhooks/subscriptions/{subscription_id}
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "events": ["application.created", "application.status_changed"],
  "active": true
}
```

### Delete Subscription
```bash
DELETE /api/webhooks/subscriptions/{subscription_id}
Authorization: Bearer YOUR_JWT_TOKEN
```

## Delivery & Retries

### Retry Policy
- **Max Retries**: 3 attempts
- **Backoff**: Exponential with jitter
  - Attempt 1: Immediate
  - Attempt 2: ~2 minutes
  - Attempt 3: ~4 minutes
  - Attempt 4: ~8 minutes

### Timeout
- **Connection Timeout**: 10 seconds
- **Read Timeout**: 30 seconds

### Expected Response
Your endpoint should:
- Return HTTP 200-299 status code for success
- Respond within 30 seconds
- Return any 2xx status (200, 201, 204, etc.)

### Delivery History
```bash
GET /api/webhooks/subscriptions/{subscription_id}/deliveries?limit=50
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "507f191e810c19729de860ea",
      "event_type": "application.created",
      "attempt": 1,
      "status": "success",
      "delivered_at": "2025-01-16T10:30:00Z",
      "response_code": 200
    },
    {
      "id": "507f191e810c19729de860eb",
      "event_type": "quiz.completed",
      "attempt": 2,
      "status": "failed",
      "delivered_at": "2025-01-16T10:32:00Z",
      "response_code": 500,
      "error": "Connection timeout"
    }
  ]
}
```

## Event Payloads

### Application Created
```json
{
  "event": "application.created",
  "data": {
    "application_id": "507f191e810c19729de860ea",
    "job_id": "...",
    "candidate_id": "...",
    "candidate_name": "John Doe",
    "candidate_email": "john@example.com",
    "job_title": "Senior Software Engineer",
    "applied_at": "2025-01-16T10:30:00Z"
  }
}
```

### Application Status Changed
```json
{
  "event": "application.status_changed",
  "data": {
    "application_id": "507f191e810c19729de860ea",
    "job_id": "...",
    "candidate_id": "...",
    "old_status": "applied",
    "new_status": "interview_scheduled",
    "changed_at": "2025-01-16T11:00:00Z",
    "changed_by": "recruiter@company.com"
  }
}
```

### Quiz Completed
```json
{
  "event": "quiz.completed",
  "data": {
    "attempt_id": "507f191e810c19729de860ea",
    "quiz_id": "...",
    "candidate_id": "...",
    "quiz_title": "Python Developer Assessment",
    "score": 85,
    "total_points": 100,
    "percentage": 85,
    "passed": true,
    "completed_at": "2025-01-16T11:15:00Z"
  }
}
```

## Security Best Practices

### 1. Always Verify Signatures
Never process webhooks without verifying the HMAC signature.

### 2. Use HTTPS
Configure your webhook endpoint with valid SSL/TLS certificate.

### 3. Rotate Secrets Regularly
Update webhook secrets periodically (every 90 days recommended).

### 4. Implement Idempotency
Handle duplicate deliveries gracefully:
```python
@app.route('/webhooks/smart-hiring', methods=['POST'])
def handle_webhook():
    delivery_id = request.headers.get('X-Webhook-Delivery-ID')
    
    # Check if already processed
    if redis_client.exists(f'webhook:{delivery_id}'):
        return {'status': 'already_processed'}, 200
    
    # Process webhook
    # ...
    
    # Mark as processed (expire after 24 hours)
    redis_client.setex(f'webhook:{delivery_id}', 86400, '1')
    
    return {'status': 'received'}, 200
```

### 5. Rate Limit Your Endpoint
Protect against potential abuse or misconfigurations.

## Monitoring & Debugging

### Subscription Statistics
```bash
GET /api/webhooks/subscriptions/{subscription_id}
```

**Response includes:**
```json
{
  "statistics": {
    "total_deliveries": 150,
    "failed_deliveries": 5,
    "success_rate": 96.67,
    "last_delivery_at": "2025-01-16T12:00:00Z",
    "delivery_breakdown": {
      "success": 145,
      "failed": 3,
      "error": 2
    }
  }
}
```

### Common Issues

#### Signature Verification Fails
- Ensure secret matches the one in subscription
- Verify payload serialization (sort keys alphabetically)
- Check character encoding (UTF-8)

#### Webhook Not Received
- Verify subscription is active
- Check firewall/security group rules
- Ensure endpoint is publicly accessible
- Review application logs for errors

#### High Failure Rate
- Subscriptions with 10+ consecutive failures are automatically disabled
- Check endpoint availability and response time
- Verify endpoint returns 2xx status codes

## Example Integrations

### Slack Notifications
```python
from slack_sdk import WebClient

@app.route('/webhooks/smart-hiring', methods=['POST'])
def webhook_to_slack():
    if not verify_webhook(request, secret):
        return {'error': 'Invalid signature'}, 401
    
    event_type = request.headers.get('X-Webhook-Event')
    data = request.get_json()['data']
    
    slack_client = WebClient(token=os.environ['SLACK_TOKEN'])
    
    if event_type == 'application.created':
        slack_client.chat_postMessage(
            channel='#recruitment',
            text=f"New application from {data['candidate_name']} for {data['job_title']}"
        )
    
    return {'status': 'received'}, 200
```

### Google Sheets Logging
```python
import gspread

@app.route('/webhooks/smart-hiring', methods=['POST'])
def webhook_to_sheets():
    if not verify_webhook(request, secret):
        return {'error': 'Invalid signature'}, 401
    
    event_type = request.headers.get('X-Webhook-Event')
    data = request.get_json()['data']
    
    gc = gspread.service_account()
    sheet = gc.open('Recruitment Tracker').sheet1
    
    if event_type == 'application.created':
        sheet.append_row([
            data['candidate_name'],
            data['job_title'],
            data['applied_at']
        ])
    
    return {'status': 'received'}, 200
```

## Testing

### Test Webhook Endpoint
```bash
# Create test subscription pointing to your local endpoint
# Use ngrok or similar to expose localhost

ngrok http 5000

# Then create subscription with ngrok URL
curl -X POST http://localhost:5000/api/webhooks/subscriptions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "url": "https://abc123.ngrok.io/webhooks/smart-hiring",
    "events": ["application.created"]
  }'
```

## Support

For webhook integration support:
- **Email**: webhooks@smarthiring.com
- **Documentation**: https://docs.smarthiring.com/webhooks
- **Status**: https://status.smarthiring.com
