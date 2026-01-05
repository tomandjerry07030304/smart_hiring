from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from bson import ObjectId
import re
import secrets
import hashlib
import os
import logging

from backend.models.database import get_db
from backend.models.user import User, Candidate
from backend.utils.sanitizer import sanitizer
from backend.utils.rate_limiter import rate_limit
from backend.utils.email_service import email_service

logger = logging.getLogger(__name__)
bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@bp.route('/register', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=3600)  # 10 registrations per hour
def register():
    """Register a new user (candidate or recruiter)"""
    try:
        print("📝 Registration attempt started")
        data = request.get_json()
        print(f"📥 Received registration data: {data}")
        
        # Validate required fields
        required_fields = ['email', 'password', 'full_name', 'role']
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing field: {field}")
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate and sanitize email
        email = sanitizer.sanitize_email(data.get('email', ''))
        if not email:
            print("❌ Invalid email format after sanitization")
            return jsonify({'error': 'Invalid email format'}), 400
        
        password = data['password']
        full_name = data['full_name'].strip()
        role = data['role'].lower()
        
        # Map 'company' to 'recruiter' if sent
        if role == 'company':
            role = 'recruiter'
        
        print(f"📧 Email: {email}, Role: {role}")
        
        # Validate email
        if not validate_email(email):
            print("❌ Email validation failed")
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate role
        if role not in ['candidate', 'recruiter', 'admin']:
            print(f"❌ Invalid role: {role}")
            return jsonify({'error': 'Invalid role. Must be candidate, recruiter, or admin'}), 400
        
        # Validate password strength (minimum 8 chars, complexity requirements)
        if len(password) < 8:
            print("❌ Password too short")
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Check password complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        if not (has_upper and has_lower and has_digit):
            print("❌ Password complexity failed")
            return jsonify({'error': 'Password must contain uppercase, lowercase, and numbers'}), 400
        
        print("✅ Validation passed, connecting to database...")
        db = get_db()
        users_collection = db['users']
        
        # Check if user already exists
        print(f"🔍 Checking if email exists: {email}")
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            print(f"❌ Email already registered: {email}")
            return jsonify({'error': 'Email already registered'}), 409
        
        print("🔒 Hashing password...")
        # Hash password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        print("👤 Creating user object...")
        # Create user
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
            full_name=full_name,
            phone=data.get('phone', ''),
            linkedin_url=data.get('linkedin_url', ''),
            github_url=data.get('github_url', '')
        )
        
        print("💾 Inserting user into database...")
        result = users_collection.insert_one(user.to_dict())
        user_id = str(result.inserted_id)
        print(f"✅ User created with ID: {user_id}")
        
        # If candidate, create candidate profile
        if role == 'candidate':
            print("📄 Creating candidate profile...")
            candidates_collection = db['candidates']
            candidate = Candidate(user_id=user_id)
            candidates_collection.insert_one(candidate.to_dict())
            print("✅ Candidate profile created")
        
        print("🎫 Generating access token...")
        # Generate JWT token
        access_token = create_access_token(identity={'user_id': user_id, 'role': role})
        
        # Send welcome email (non-blocking)
        try:
            email_service.send_welcome_email(email, full_name, role)
        except Exception as email_error:
            print(f"⚠️ Welcome email failed: {email_error}")
        
        print(f"🎉 Registration successful for {email}")
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'access_token': access_token,
            'user': {
                'email': email,
                'full_name': full_name,
                'role': role
            }
        }), 201
        
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=300)  # 5 attempts per 5 minutes
def login():
    """Login user"""
    try:
        print("🔐 Login attempt started")
        data = request.get_json()
        print(f"📥 Received data: {data.get('email', 'no email')} (password hidden)")
        
        if 'email' not in data or 'password' not in data:
            print("❌ Missing email or password")
            return jsonify({'error': 'Email and password required'}), 400
        
        # Sanitize inputs
        print("🧹 Sanitizing email...")
        email = sanitizer.sanitize_email(data['email'])
        if not email:
            print("❌ Email validation failed")
            return jsonify({'error': 'Invalid email format'}), 400
        
        print(f"✅ Email sanitized: {email}")
        password = data['password']
        
        print("🔌 Connecting to database...")
        db = get_db()
        users_collection = db['users']
        
        # Find user
        print(f"🔍 Looking up user: {email}")
        user = users_collection.find_one({'email': email})
        if not user:
            print("❌ User not found")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        print(f"✅ User found: {user.get('email')} (role: {user.get('role')})")
        
        # Check if password_hash exists
        if 'password_hash' not in user:
            print("❌ No password_hash in user document")
            return jsonify({'error': 'Account configuration error. Please contact administrator.'}), 500
        
        print("🔒 Checking password...")
        # Check password
        if not bcrypt.check_password_hash(user['password_hash'], password):
            print("❌ Password check failed")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        print("✅ Password correct")
        
        # Check if user is active
        if not user.get('is_active', True):
            print("❌ User account is deactivated")
            return jsonify({'error': 'Account is deactivated'}), 403
        
        print("🎫 Generating JWT token...")
        # Generate JWT token with user_id as identity and role as additional claim
        access_token = create_access_token(
            identity=str(user['_id']),
            additional_claims={'role': user['role']}
        )
        
        print("✅ Login successful!")
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'user_id': str(user['_id']),
                'email': user['email'],
                'full_name': user['full_name'],
                'role': user['role'],
                'profile_completed': user.get('profile_completed', False)
            }
        }), 200
        
    except KeyError as e:
        # Specific handling for missing keys
        print(f"KeyError in login: {str(e)}")
        return jsonify({'error': f'Account data error: missing {str(e)}'}), 500
    except Exception as e:
        # General exception handling
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']
        
        db = get_db()
        users_collection = db['users']
        
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Remove sensitive data
        user['_id'] = str(user['_id'])
        del user['password_hash']
        
        return jsonify(user), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/forgot-password', methods=['POST'])
@rate_limit(max_requests=3, window_seconds=3600)  # 3 requests per hour
def forgot_password():
    """Request password reset - generates reset token"""
    try:
        data = request.get_json()
        
        if 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].lower().strip()
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        db = get_db()
        users_collection = db['users']
        
        # Check if user exists
        user = users_collection.find_one({'email': email})
        
        if not user:
            # Return success even if user doesn't exist (security best practice)
            return jsonify({
                'message': 'If an account exists with this email, a password reset link has been sent',
                'note': 'Email functionality not configured - use reset token below for testing'
            }), 200
        
        # Generate reset token (valid for 1 hour)
        reset_token = secrets.token_urlsafe(32)
        reset_token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
        reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        
        # Store reset token in database
        users_collection.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'reset_token': reset_token_hash,
                    'reset_token_expires': reset_token_expires,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        # Send password reset email
        base_url = os.getenv('FRONTEND_URL', 'http://localhost:5000')
        reset_link = f"{base_url}/reset-password.html?token={reset_token}&email={email}"
        
        # Send email with reset link
        from backend.utils.email_service import email_service
        email_sent = False
        try:
            email_sent = email_service.send_password_reset_email(
                to_email=email,
                reset_link=reset_link,
                user_name=user.get('name', email)
            )
        except Exception as email_error:
            logger.warning(f"Failed to send password reset email: {email_error}")
        
        # Build response with development info if emails are disabled
        response_data = {
            'message': 'If an account exists with this email, password reset instructions have been sent'
        }
        
        # In development mode or when emails are disabled, include the reset token for testing
        email_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
        if not email_enabled or current_app.config.get('DEBUG', False):
            print(f"[DEV MODE] Password reset token for {email}: {reset_token}")
            print(f"[DEV MODE] Reset link: {reset_link}")
            response_data['dev_mode'] = True
            response_data['reset_token'] = reset_token
            response_data['reset_link'] = reset_link
            response_data['email_sent'] = email_sent
            response_data['note'] = 'Email notifications are currently disabled. Use the reset token and link below for testing.'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using reset token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'reset_token', 'new_password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        email = data['email'].lower().strip()
        reset_token = data['reset_token']
        new_password = data['new_password']
        
        # Validate email
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate new password strength (minimum 8 chars, complexity requirements)
        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Check password complexity
        has_upper = any(c.isupper() for c in new_password)
        has_lower = any(c.islower() for c in new_password)
        has_digit = any(c.isdigit() for c in new_password)
        
        if not (has_upper and has_lower and has_digit):
            return jsonify({'error': 'Password must contain uppercase, lowercase, and numbers'}), 400
        
        db = get_db()
        users_collection = db['users']
        
        # Hash the provided token
        reset_token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
        
        # Find user with matching email and valid reset token
        user = users_collection.find_one({
            'email': email,
            'reset_token': reset_token_hash,
            'reset_token_expires': {'$gt': datetime.utcnow()}
        })
        
        if not user:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        # Hash new password
        new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        # Update password and clear reset token
        users_collection.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'password_hash': new_password_hash,
                    'updated_at': datetime.utcnow()
                },
                '$unset': {
                    'reset_token': '',
                    'reset_token_expires': ''
                }
            }
        )
        
        return jsonify({
            'message': 'Password reset successfully',
            'success': True
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for logged-in user"""
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['current_password', 'new_password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Validate new password strength (minimum 8 chars, complexity requirements)
        if len(new_password) < 8:
            return jsonify({'error': 'New password must be at least 8 characters'}), 400
        
        # Check password complexity
        has_upper = any(c.isupper() for c in new_password)
        has_lower = any(c.islower() for c in new_password)
        has_digit = any(c.isdigit() for c in new_password)
        
        if not (has_upper and has_lower and has_digit):
            return jsonify({'error': 'Password must contain uppercase, lowercase, and numbers'}), 400
        
        if current_password == new_password:
            return jsonify({'error': 'New password must be different from current password'}), 400
        
        db = get_db()
        users_collection = db['users']
        
        # Get user
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not bcrypt.check_password_hash(user['password_hash'], current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Hash new password
        new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        # Update password
        users_collection.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'password_hash': new_password_hash,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        return jsonify({
            'message': 'Password changed successfully',
            'success': True
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user = get_jwt_identity()
        user_id = current_user['user_id']
        data = request.get_json()
        
        db = get_db()
        users_collection = db['users']
        
        # Fields that can be updated
        allowed_fields = ['full_name', 'phone', 'linkedin_url', 'github_url']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        update_data['updated_at'] = datetime.utcnow()
        
        result = users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            return jsonify({'message': 'Profile updated successfully'}), 200
        else:
            return jsonify({'message': 'No changes made'}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
