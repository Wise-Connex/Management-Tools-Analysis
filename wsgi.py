#!/usr/bin/env python3
"""
WSGI entry point for the Management Tools Analysis Dashboard.
This file provides the proper WSGI application for production deployment.
"""

# Import the Flask server from the dashboard app
from dashboard_app.app import server

# The server variable is the Flask application instance
application = server

if __name__ == '__main__':
    # For local testing
    application.run(
        debug=False,
        host='0.0.0.0',
        port=8050
    )