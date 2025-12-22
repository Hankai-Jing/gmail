"""
REST API for the Gmail-like system.
Provides endpoints for iOS, Android, and web clients.
"""
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
import datetime
import os

# Create API blueprint
api = Blueprint('api', __name__, url_prefix='/api/v1')

# JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days


def get_email_service():
    """Get email service from app context."""
    return current_app.config['email_service']



def create_access_token(email_address: str) -> str:
    """Create a JWT access token."""
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        'email': email_address,
        'exp': expiration,
        'type': 'access'
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(email_address: str) -> str:
    """Create a JWT refresh token."""
    expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        'email': email_address,
        'exp': expiration,
        'type': 'refresh'
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def token_required(f):
    """Decorator to require JWT token for protected endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode token
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Check token type
            if payload.get('type') != 'access':
                return jsonify({'error': 'Invalid token type'}), 401
            
            # Get user email from token
            current_user_email = payload['email']
            
            # Verify user exists
            if not get_email_service().storage.user_exists(current_user_email):
                return jsonify({'error': 'User not found'}), 401
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Pass user email to the endpoint
        return f(current_user_email, *args, **kwargs)
    
    return decorated


# Authentication endpoints

@api.route('/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email_address = data.get('email')
    name = data.get('name')
    
    if not email_address or not name:
        return jsonify({'error': 'Email and name are required'}), 400
    
    try:
        user = get_email_service().register_user(email_address, name)
        
        # Create tokens
        access_token = create_access_token(user.email_address)
        refresh_token = create_refresh_token(user.email_address)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/auth/login', methods=['POST'])
def login():
    """Login a user (simple email-based login, no password)."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email_address = data.get('email')
    
    if not email_address:
        return jsonify({'error': 'Email is required'}), 400
    
    # Check if user exists
    user = get_email_service().get_user(email_address)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Create tokens
    access_token = create_access_token(user.email_address)
    refresh_token = create_refresh_token(user.email_address)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@api.route('/auth/refresh', methods=['POST'])
def refresh():
    """Refresh access token using refresh token."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({'error': 'Refresh token is required'}), 400
    
    try:
        # Decode refresh token
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check token type
        if payload.get('type') != 'refresh':
            return jsonify({'error': 'Invalid token type'}), 401
        
        email_address = payload['email']
        
        # Create new access token
        new_access_token = create_access_token(email_address)
        
        return jsonify({
            'access_token': new_access_token
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Refresh token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid refresh token'}), 401


# Email endpoints

@api.route('/emails', methods=['POST'])
@token_required
def send_email(current_user_email):
    """Send an email."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    recipient = data.get('recipient')
    subject = data.get('subject')
    body = data.get('body')
    
    if not recipient or not subject or not body:
        return jsonify({'error': 'Recipient, subject, and body are required'}), 400
    
    try:
        email = get_email_service().send_email(current_user_email, recipient, subject, body)
        
        return jsonify({
            'message': 'Email sent successfully',
            'email': email.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/emails/inbox', methods=['GET'])
@token_required
def get_inbox(current_user_email):
    """Get inbox emails for current user."""
    try:
        emails = get_email_service().get_inbox(current_user_email)
        
        return jsonify({
            'emails': [email.to_dict() for email in emails],
            'count': len(emails)
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/emails/sent', methods=['GET'])
@token_required
def get_sent(current_user_email):
    """Get sent emails for current user."""
    try:
        emails = get_email_service().get_sent(current_user_email)
        
        return jsonify({
            'emails': [email.to_dict() for email in emails],
            'count': len(emails)
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/emails/<email_id>', methods=['GET'])
@token_required
def get_email(current_user_email, email_id):
    """Get a specific email."""
    email = get_email_service().storage.get_email(email_id)
    
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    # Check authorization
    if email.sender != current_user_email and email.recipient != current_user_email:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'email': email.to_dict()
    }), 200


@api.route('/emails/<email_id>/read', methods=['PUT'])
@token_required
def mark_email_read(current_user_email, email_id):
    """Mark an email as read."""
    try:
        email = get_email_service().read_email(email_id, current_user_email)
        
        if not email:
            return jsonify({'error': 'Email not found'}), 404
        
        return jsonify({
            'message': 'Email marked as read',
            'email': email.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 403


# User endpoints

@api.route('/users', methods=['GET'])
@token_required
def get_users(current_user_email):
    """Get all registered users."""
    users = get_email_service().list_users()
    
    return jsonify({
        'users': [user.to_dict() for user in users],
        'count': len(users)
    }), 200


@api.route('/users/me', methods=['GET'])
@token_required
def get_current_user(current_user_email):
    """Get current user information."""
    user = get_email_service().get_user(current_user_email)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict()
    }), 200


# Health check endpoint

@api.route('/health', methods=['GET'])
def health_check():
    """API health check."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'api': 'v1'
    }), 200
