"""
WSGI Entry Point for Render (Gunicorn)
"""
from app import app

# Gunicorn on Render requires the app to be named 'app' or exposed via this file
if __name__ == "__main__":
    app.run()
