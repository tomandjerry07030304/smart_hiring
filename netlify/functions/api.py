"""
Netlify serverless function entry point
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

from backend.app import app

def handler(event, context):
    """
    Netlify function handler
    """
    # For Netlify Functions, we need to use the serverless WSGI adapter
    try:
        from werkzeug.wrappers import Request, Response
        from werkzeug.serving import run_simple
        
        # Convert Netlify event to WSGI environ
        environ = {
            'REQUEST_METHOD': event.get('httpMethod', 'GET'),
            'SCRIPT_NAME': '',
            'PATH_INFO': event.get('path', '/'),
            'QUERY_STRING': event.get('queryStringParameters', ''),
            'SERVER_NAME': 'netlify',
            'SERVER_PORT': '443',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': event.get('body', ''),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        # Add headers
        for key, value in event.get('headers', {}).items():
            key = 'HTTP_' + key.upper().replace('-', '_')
            environ[key] = value
        
        # Call Flask app
        with app.request_context(environ):
            response = app.full_dispatch_request()
            
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
