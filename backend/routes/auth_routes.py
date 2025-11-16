from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime
from bson import ObjectId
import re

from backend.models.database import get_db
from backend.models.user import User, Candidate

bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user (candidate or recruiter)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'full_name', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        full_name = data['full_name'].strip()
        role = data['role'].lower()
        
        # Validate email
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate role
        if role not in ['candidate', 'recruiter', 'admin']:
            return jsonify({'error': 'Invalid role. Must be candidate, recruiter, or admin'}), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        db = get_db()
        users_collection = db['users']
        
        # Check if user already exists
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
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
        
        result = users_collection.insert_one(user.to_dict())
        user_id = str(result.inserted_id)
        
        # If candidate, create candidate profile
        if role == 'candidate':
            candidates_collection = db['candidates']
            candidate = Candidate(user_id=user_id)
            candidates_collection.insert_one(candidate.to_dict())
        
        # Generate JWT token
        access_token = create_access_token(identity={'user_id': user_id, 'role': role})
        
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
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        db = get_db()
        users_collection = db['users']
        
        # Find user
        user = users_collection.find_one({'email': email})
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if password_hash exists
        if 'password_hash' not in user:
            return jsonify({'error': 'Account configuration error. Please contact administrator.'}), 500
        
        # Check password
        if not bcrypt.check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is active
        if not user.get('is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Generate JWT token
        access_token = create_access_token(
            identity={
                'user_id': str(user['_id']),
                'role': user['role']
            }
        )
        
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
