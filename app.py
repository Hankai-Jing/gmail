"""
Flask web application for the Gmail-like system.
Includes both traditional web UI and REST API for mobile platforms.
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_cors import CORS
from email_service import EmailService
from database_storage import DatabaseStorage
import os


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize with database storage
storage = DatabaseStorage('gmail.db')
email_service = EmailService(storage)

# Store email_service in app config for API access
app.config['email_service'] = email_service

# Register API blueprint
from api import api
app.register_blueprint(api)

# Enable CORS for API endpoints only
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/')
def index():
    """Home page."""
    current_user = session.get('user_email')
    if current_user:
        return redirect(url_for('inbox'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if request.method == 'POST':
        email_address = request.form.get('email_address', '').strip()
        name = request.form.get('name', '').strip()
        
        if not email_address or not name:
            flash('Email address and name are required', 'error')
            return render_template('register.html')
        
        try:
            email_service.register_user(email_address, name)
            flash(f'Successfully registered {name}!', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('register.html')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if request.method == 'POST':
        email_address = request.form.get('email_address', '').strip()
        
        if not email_address:
            flash('Email address is required', 'error')
            return render_template('login.html')
        
        user = email_service.get_user(email_address)
        if user:
            session['user_email'] = user.email_address
            session['user_name'] = user.name
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('inbox'))
        else:
            flash('User not found. Please register first.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout the current user."""
    session.pop('user_email', None)
    session.pop('user_name', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/inbox')
def inbox():
    """View inbox."""
    current_user = session.get('user_email')
    if not current_user:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    inbox_emails = email_service.get_inbox(current_user)
    return render_template('inbox.html', emails=inbox_emails, current_user=current_user)


@app.route('/sent')
def sent():
    """View sent emails."""
    current_user = session.get('user_email')
    if not current_user:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    sent_emails = email_service.get_sent(current_user)
    return render_template('sent.html', emails=sent_emails, current_user=current_user)


@app.route('/compose', methods=['GET', 'POST'])
def compose():
    """Compose and send a new email."""
    current_user = session.get('user_email')
    if not current_user:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        recipient = request.form.get('recipient', '').strip()
        subject = request.form.get('subject', '').strip()
        body = request.form.get('body', '').strip()
        
        if not recipient or not subject or not body:
            flash('All fields are required', 'error')
            return render_template('compose.html', users=email_service.list_users())
        
        try:
            email_service.send_email(current_user, recipient, subject, body)
            flash('Email sent successfully!', 'success')
            return redirect(url_for('sent'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('compose.html', users=email_service.list_users())
    
    users = email_service.list_users()
    return render_template('compose.html', users=users, current_user=current_user)


@app.route('/email/<email_id>')
def view_email(email_id):
    """View a specific email."""
    current_user = session.get('user_email')
    if not current_user:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    email = storage.get_email(email_id)
    
    if not email:
        flash('Email not found', 'error')
        return redirect(url_for('inbox'))
    
    # Check if user is authorized to view this email
    if email.sender != current_user and email.recipient != current_user:
        flash('You are not authorized to view this email', 'error')
        return redirect(url_for('inbox'))
    
    # Mark as read if user is the recipient
    if email.recipient == current_user and not email.read:
        try:
            email_service.read_email(email_id, current_user)
            email = storage.get_email(email_id)  # Refresh to get updated read status
        except ValueError:
            pass
    
    return render_template('view_email.html', email=email, current_user=current_user)


@app.route('/users')
def users():
    """View all registered users."""
    current_user = session.get('user_email')
    if not current_user:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    all_users = email_service.list_users()
    return render_template('users.html', users=all_users, current_user=current_user)


if __name__ == '__main__':
    # Debug mode should only be enabled in development
    # Set FLASK_DEBUG=1 environment variable for debug mode
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    port = int(os.environ.get('FLASK_PORT', '5000'))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
