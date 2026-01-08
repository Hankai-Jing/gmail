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
    # Get port from environment variable, default to 5000
    port = int(os.environ.get('FLASK_PORT', '5000'))
    
    print("=" * 80)
    print("Gmail-like System - Web Interface")
    print("=" * 80)
    print("\nStarting Flask web server...")
    print(f"Open your browser and navigate to: http://localhost:{port}")
    print("\nPress CTRL+C to stop the server")
    print("\nNote: Set FLASK_DEBUG=1 environment variable to enable debug mode")
    print("Note: Set FLASK_PORT environment variable to change the port (default: 5000)")
    print("      Example: FLASK_PORT=8080 python run_web.py")
    print("=" * 80)
    
    # Debug mode should only be enabled in development
    # Set FLASK_DEBUG=1 environment variable for debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
