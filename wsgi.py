"""
Production WSGI Entrypoint for LAK04 Web Application.
Compatible with Gunicorn, Waitress, uWSGI, and cloud platforms
(Render, PythonAnywhere, Railway, Heroku).
"""

from app import app
from models import init_db

# Ensure tables are initialized on startup
init_db()

if __name__ == "__main__":
    app.run()
