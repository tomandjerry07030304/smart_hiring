"""
Smart Hiring System - Main Application Entry Point
Initializes Flask app with all routes and configurations
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config.config import config
from backend.models.database import Database
from backend.routes import auth_routes, job_routes, candidate_routes, assessment_routes, dashboard_routes

# Initialize Flask app with frontend folder
frontend_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app = Flask(__name__, static_folder=frontend_folder, static_url_path='')

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)

# Initialize database connection
db = Database()
db.connect(env)

# Register blueprints (API routes)
app.register_blueprint(auth_routes.bp, url_prefix='/api/auth')
app.register_blueprint(job_routes.bp, url_prefix='/api/jobs')
app.register_blueprint(candidate_routes.bp, url_prefix='/api/candidates')
app.register_blueprint(assessment_routes.bp, url_prefix='/api/assessments')
app.register_blueprint(dashboard_routes.bp, url_prefix='/api/dashboard')

# Root endpoint - serve frontend
@app.route('/')
def home():
    """Serve the frontend application"""
    return send_from_directory(app.static_folder, 'index.html')

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
