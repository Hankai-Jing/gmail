#!/usr/bin/env python3
"""
Start the Gmail-like web application.
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    print("=" * 80)
    print("Gmail-like System - Web Interface")
    print("=" * 80)
    print("\nStarting Flask web server...")
    print("Open your browser and navigate to: http://localhost:5000")
    print("\nPress CTRL+C to stop the server")
    print("\nNote: Set FLASK_DEBUG=1 environment variable to enable debug mode")
    print("=" * 80)
    
    # Debug mode should only be enabled in development
    # Set FLASK_DEBUG=1 environment variable for debug mode
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
