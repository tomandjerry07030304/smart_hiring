"""
Smart Hiring System - Main Application Entry Point
Version: 2.0.0 - Enterprise Edition with Security, Workers, GDPR Compliance
Initializes Flask app with all routes and configurations
© 2025 Smart Hiring System - Proprietary Software - All Rights Reserved
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config.config import config
from backend.models.database import Database
from backend.routes import auth_routes, job_routes, candidate_routes, company_routes, email_preferences_routes, assessment_routes, audit_routes, dsr_routes, dashboard_routes, ai_interview_routes, admin_routes
# Import enhanced v2 routes
try:
    from backend.routes import ai_interview_routes_v2
    V2_ROUTES_AVAILABLE = True
except ImportError:
    V2_ROUTES_AVAILABLE = False
    print("⚠️ V2 routes not available (requires requests-oauthlib). Install with: pip install requests-oauthlib")
    
from backend.utils.license_validator import check_deployment_authorization, require_valid_license
from backend.utils.env_config import env_config, print_startup_banner
from backend.utils.monitoring import initialize_monitoring
from backend.workers.job_processor import start_workers, stop_workers
import atexit
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, env_config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# DEPLOYMENT AUTHORIZATION CHECK (Optional - can be disabled for cloud deployments)
# Uncomment the following lines to enable license validation:
# if not check_deployment_authorization():
#     print("\n🚨 CRITICAL: Unauthorized deployment detected")
#     print("This software is proprietary and requires a valid license.")
#     print("Contact: mightyazad@gmail.com or admin@smarthiring.com")
#     sys.exit(1)

# Initialize Flask app with frontend folder
frontend_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app = Flask(__name__, static_folder=frontend_folder, static_url_path='')

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize extensions
# SECURITY: Configure CORS properly for production
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
CORS(app, 
     resources={r"/api/*": {
         "origins": allowed_origins,
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True,
         "max_age": 3600
     }})

# Initialize JWT Manager  
jwt = JWTManager(app)

# Security headers
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'"
    return response

# Initialize database connection
db = Database()
db.connect(env)

# Auto-create test accounts on startup (for production deployment)
def create_default_accounts():
    """Create default test accounts if they don't exist"""
    try:
        from werkzeug.security import generate_password_hash
        from datetime import datetime
        
        users_collection = db.get_collection('users')
        if users_collection is None:
            print("⚠️ Could not get users collection")
            return
        
        default_accounts = [
            {
                'email': 'admin@smarthiring.com',
                'password': generate_password_hash('Admin@123'),
                'name': 'System Admin',
                'role': 'admin',
                'is_active': True,
                'created_at': datetime.utcnow(),
                'email_verified': True
            },
            {
                'email': 'recruiter@test.com',
                'password': generate_password_hash('password123'),
                'name': 'Test Recruiter',
                'role': 'company',
                'company_name': 'Test Company Inc.',
                'is_active': True,
                'created_at': datetime.utcnow(),
                'email_verified': True
            },
            {
                'email': 'candidate@test.com',
                'password': generate_password_hash('password123'),
                'name': 'Test Candidate',
                'role': 'candidate',
                'is_active': True,
                'created_at': datetime.utcnow(),
                'email_verified': True
            }
        ]
        
        created_count = 0
        for account in default_accounts:
            existing = users_collection.find_one({'email': account['email']})
            if not existing:
                users_collection.insert_one(account)
                print(f"✅ Created default account: {account['email']}")
                created_count += 1
            else:
                print(f"ℹ️ Account already exists: {account['email']}")
        
        if created_count > 0:
            print(f"🎉 Created {created_count} default account(s)")
        else:
            print("ℹ️ All default accounts already exist")
            
    except Exception as e:
        print(f"⚠️ Could not create default accounts: {e}")

# Create default accounts on startup
create_default_accounts()

# Register blueprints (API routes)
app.register_blueprint(auth_routes.bp, url_prefix='/api/auth')
app.register_blueprint(job_routes.bp, url_prefix='/api/jobs')
app.register_blueprint(candidate_routes.bp, url_prefix='/api/candidates')
app.register_blueprint(company_routes.bp, url_prefix='/api/company')
app.register_blueprint(email_preferences_routes.bp, url_prefix='/api/email')
app.register_blueprint(assessment_routes.bp, url_prefix='/api/assessments')
app.register_blueprint(audit_routes.bp, url_prefix='/api/audit')
app.register_blueprint(dsr_routes.bp, url_prefix='/api/dsr')
app.register_blueprint(dashboard_routes.bp, url_prefix='/api/dashboard')
app.register_blueprint(ai_interview_routes.bp, url_prefix='/api/ai-interview')
app.register_blueprint(admin_routes.bp, url_prefix='/api/admin')

# Register V2 routes if available (LinkedIn, dynamic questions, fresher scoring)
if V2_ROUTES_AVAILABLE:
    app.register_blueprint(ai_interview_routes_v2.bp, url_prefix='/api/ai-interview-v2')
    print("✅ Enhanced V2 routes registered: LinkedIn integration, dynamic questions, fresher scoring")

# Initialize monitoring & observability
initialize_monitoring(app)

# Start background workers if enabled
if env_config.enable_background_workers and env_config.enable_redis:
    try:
        logger.info("🚀 Starting background workers...")
        start_workers(num_workers=env_config.num_workers)
        
        # Register cleanup on shutdown
        def cleanup_workers():
            logger.info("🛑 Stopping background workers...")
            stop_workers()
        
        atexit.register(cleanup_workers)
        logger.info(f"✅ {env_config.num_workers} background workers started")
    except Exception as e:
        logger.warning(f"⚠️ Failed to start workers: {e}. Continuing without workers...")
else:
    logger.info("ℹ️ Background workers disabled (enable with ENABLE_BACKGROUND_WORKERS=true and Redis)")

# Root endpoint - serve frontend
@app.route('/')
def home():
    """Serve the frontend application"""
    try:
        print(f"🏠 Serving index.html from: {app.static_folder}")
        print(f"📁 Static folder exists: {os.path.exists(app.static_folder)}")
        index_path = os.path.join(app.static_folder, 'index.html')
        print(f"📄 Index.html exists: {os.path.exists(index_path)}")
        return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        print(f"❌ Error serving index.html: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to serve frontend', 'details': str(e)}), 500

# Catch-all route for frontend - serve index.html for any non-API routes
@app.route('/<path:path>')
def catch_all(path):
    """Serve frontend for all non-API routes"""
    try:
        # If it's an API request that doesn't exist, return 404 JSON
        if path.startswith('api/'):
            return jsonify({'error': 'API endpoint not found'}), 404
        
        # Try to serve the requested file
        file_path = os.path.join(app.static_folder, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(app.static_folder, path)
        else:
            # If file doesn't exist, serve index.html (for client-side routing)
            return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        print(f"❌ Error in catch_all for path '{path}': {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to serve resource', 'path': path}), 500

# API info endpoint
@app.route('/api')
def api_info():
    """API information"""
    return jsonify({
        'message': 'Smart Hiring System API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'jobs': '/api/jobs',
            'candidates': '/api/candidates',
            'assessments': '/api/assessments',
            'dashboard': '/api/dashboard'
        },
        'documentation': 'See API_DOCUMENTATION.md for details'
    })

# Health check endpoint
@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'environment': env
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Print startup banner
    print_startup_banner()
    
    # Start Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=env_config.debug,
        use_reloader=False,
        threaded=True
    )

# Export app for Vercel
application = app
