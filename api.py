"""
REST API for the Gmail-like system.
Provides endpoints for iOS, Android, and web clients.
"""
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
import datetime
import os
from observability import LOGGER, METRICS, log_event, get_request_id, hash_email

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
                METRICS.inc_counter("auth_token_total", labels={"status": "error", "reason": "invalid_header"})
                log_event(
                    LOGGER,
                    "auth.token",
                    request_id=get_request_id(),
                    status="error",
                    reason="invalid_header",
                )
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        if not token:
            METRICS.inc_counter("auth_token_total", labels={"status": "error", "reason": "missing"})
            log_event(
                LOGGER,
                "auth.token",
                request_id=get_request_id(),
                status="error",
                reason="missing",
            )
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode token
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Check token type
            if payload.get('type') != 'access':
                METRICS.inc_counter("auth_token_total", labels={"status": "error", "reason": "invalid_type"})
                log_event(
                    LOGGER,
                    "auth.token",
                    request_id=get_request_id(),
                    status="error",
                    reason="invalid_type",
                )
                return jsonify({'error': 'Invalid token type'}), 401
            
            # Get user email from token
            current_user_email = payload['email']
            
            # Verify user exists
            if not get_email_service().storage.user_exists(current_user_email):
                METRICS.inc_counter("auth_token_total", labels={"status": "error", "reason": "user_missing"})
                log_event(
                    LOGGER,
                    "auth.token",
                    request_id=get_request_id(),
                    status="error",
                    reason="user_missing",
                    user_hash=hash_email(current_user_email),
                )
                return jsonify({'error': 'User not found'}), 401
            
        except jwt.ExpiredSignatureError:
            METRICS.inc_counter("auth_token_total", labels={"status": "error", "reason": "expired"})
            log_event(
                LOGGER,
                "auth.token",
                request_id=get_request_id(),
                status="error",
                reason="expired",
            )
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            METRICS.inc_counter("auth_token_total", labels={"status": "error", "reason": "invalid"})
            log_event(
                LOGGER,
                "auth.token",
                request_id=get_request_id(),
                status="error",
                reason="invalid",
            )
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
        METRICS.inc_counter("auth_register_total", labels={"status": "error", "reason": "no_data"})
        return jsonify({'error': 'No data provided'}), 400
    
    email_address = data.get('email')
    name = data.get('name')
    
    if not email_address or not name:
        METRICS.inc_counter("auth_register_total", labels={"status": "error", "reason": "missing_fields"})
        return jsonify({'error': 'Email and name are required'}), 400
    
    try:
        user = get_email_service().register_user(email_address, name)
        
        # Create tokens
        access_token = create_access_token(user.email_address)
        refresh_token = create_refresh_token(user.email_address)
        
        METRICS.inc_counter("auth_register_total", labels={"status": "success"})
        log_event(
            LOGGER,
            "auth.register",
            request_id=get_request_id(),
            status="success",
            user_hash=hash_email(user.email_address),
        )
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except ValueError as e:
        METRICS.inc_counter("auth_register_total", labels={"status": "error", "reason": "invalid"})
        log_event(
            LOGGER,
            "auth.register",
            request_id=get_request_id(),
            status="error",
            reason="invalid",
            user_hash=hash_email(email_address),
        )
        return jsonify({'error': str(e)}), 400


@api.route('/auth/login', methods=['POST'])
def login():
    """Login a user (simple email-based login, no password)."""
    data = request.get_json()
    
    if not data:
        METRICS.inc_counter("auth_login_total", labels={"status": "error", "reason": "no_data"})
        return jsonify({'error': 'No data provided'}), 400
    
    email_address = data.get('email')
    
    if not email_address:
        METRICS.inc_counter("auth_login_total", labels={"status": "error", "reason": "missing_email"})
        return jsonify({'error': 'Email is required'}), 400
    
    # Check if user exists
    user = get_email_service().get_user(email_address)
    
    if not user:
        METRICS.inc_counter("auth_login_total", labels={"status": "error", "reason": "not_found"})
        log_event(
            LOGGER,
            "auth.login",
            request_id=get_request_id(),
            status="error",
            reason="not_found",
            user_hash=hash_email(email_address),
        )
        return jsonify({'error': 'User not found'}), 404
    
    # Create tokens
    access_token = create_access_token(user.email_address)
    refresh_token = create_refresh_token(user.email_address)
    
    METRICS.inc_counter("auth_login_total", labels={"status": "success"})
    log_event(
        LOGGER,
        "auth.login",
        request_id=get_request_id(),
        status="success",
        user_hash=hash_email(user.email_address),
    )
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
        METRICS.inc_counter("auth_refresh_total", labels={"status": "error", "reason": "no_data"})
        return jsonify({'error': 'No data provided'}), 400
    
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        METRICS.inc_counter("auth_refresh_total", labels={"status": "error", "reason": "missing_token"})
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
        
        METRICS.inc_counter("auth_refresh_total", labels={"status": "success"})
        log_event(
            LOGGER,
            "auth.refresh",
            request_id=get_request_id(),
            status="success",
        )
        return jsonify({
            'access_token': new_access_token
        }), 200
        
    except jwt.ExpiredSignatureError:
        METRICS.inc_counter("auth_refresh_total", labels={"status": "error", "reason": "expired"})
        return jsonify({'error': 'Refresh token has expired'}), 401
    except jwt.InvalidTokenError:
        METRICS.inc_counter("auth_refresh_total", labels={"status": "error", "reason": "invalid"})
        return jsonify({'error': 'Invalid refresh token'}), 401


# Email endpoints

@api.route('/emails', methods=['POST'])
@token_required
def send_email(current_user_email):
    """Send an email."""
    data = request.get_json()
    
    if not data:
        METRICS.inc_counter("emails_send_requests_total", labels={"status": "error", "reason": "no_data"})
        return jsonify({'error': 'No data provided'}), 400
    
    recipient = data.get('recipient')
    subject = data.get('subject')
    body = data.get('body')
    
    if not recipient or not subject or not body:
        METRICS.inc_counter("emails_send_requests_total", labels={"status": "error", "reason": "missing_fields"})
        return jsonify({'error': 'Recipient, subject, and body are required'}), 400
    
    try:
        email = get_email_service().send_email(current_user_email, recipient, subject, body)
        
        METRICS.inc_counter("emails_send_requests_total", labels={"status": "success"})
        return jsonify({
            'message': 'Email sent successfully',
            'email': email.to_dict()
        }), 201
        
    except ValueError as e:
        METRICS.inc_counter("emails_send_requests_total", labels={"status": "error", "reason": "invalid"})
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


# Root and health check endpoints

@api.route('/', methods=['GET'])
def api_root():
    """API root endpoint - provides API information."""
    return jsonify({
        'message': 'Gmail-like System REST API',
        'version': '1.0.0',
        'api': 'v1',
        'endpoints': {
            'authentication': {
                'register': 'POST /api/v1/auth/register',
                'login': 'POST /api/v1/auth/login',
                'refresh': 'POST /api/v1/auth/refresh'
            },
            'emails': {
                'send': 'POST /api/v1/emails',
                'inbox': 'GET /api/v1/emails/inbox',
                'sent': 'GET /api/v1/emails/sent',
                'get': 'GET /api/v1/emails/<email_id>',
                'mark_read': 'PUT /api/v1/emails/<email_id>/read'
            },
            'users': {
                'list': 'GET /api/v1/users',
                'me': 'GET /api/v1/users/me'
            },
            'health': 'GET /api/v1/health'
        },
        'documentation': 'See API_DOCUMENTATION.md for complete API reference'
    }), 200


@api.route('/health', methods=['GET'])
def health_check():
    """API health check."""
    storage = get_email_service().storage
    db_ok = True
    if hasattr(storage, "health_check"):
        db_ok = storage.health_check()
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'api': 'v1',
        'db': 'ok' if db_ok else 'error'
    }), 200
