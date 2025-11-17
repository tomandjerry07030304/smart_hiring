"""
Smart Hiring System - Main Application Entry Point
Version: 1.2.0 - JWT Fix Applied + MongoDB Connected
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
from backend.routes import auth_routes, job_routes, candidate_routes
from backend.utils.license_validator import check_deployment_authorization, require_valid_license
# Disabled for Render free tier: assessment_routes, dashboard_routes (require ML libraries)

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

# Register blueprints (API routes)
app.register_blueprint(auth_routes.bp, url_prefix='/api/auth')
app.register_blueprint(job_routes.bp, url_prefix='/api/jobs')
app.register_blueprint(candidate_routes.bp, url_prefix='/api/candidates')
# Disabled for Render free tier (require ML libraries):
# app.register_blueprint(assessment_routes.bp, url_prefix='/api/assessments')
# app.register_blueprint(dashboard_routes.bp, url_prefix='/api/dashboard')

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
    print("\n" + "="*60)
    print("🚀 Starting Smart Hiring System API")
    print("="*60)
    print(f"📍 Environment: {env}")
    print(f"🔗 Running on: http://localhost:5000")
    print(f"🗄️  Database: {app.config['DB_NAME']}")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False,
        threaded=True
    )

# Export app for Vercel
application = app
