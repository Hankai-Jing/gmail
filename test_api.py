"""
Unit tests for the REST API.
"""
import unittest
import json
import os
from app import app
from database_storage import DatabaseStorage
from email_service import EmailService


class TestAPI(unittest.TestCase):
    """Test cases for REST API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use test database
        self.test_db = "test_api_gmail.db"
        os.environ['JWT_SECRET'] = 'test-secret-key'
        
        # Clear any existing test database
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        
        # Create fresh storage and service for testing
        test_storage = DatabaseStorage(self.test_db)
        test_service = EmailService(test_storage)
        
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['email_service'] = test_service
        self.client = app.test_client()
    
    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_api_root(self):
        """Test API root endpoint."""
        response = self.client.get('/api/v1/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('version', data)
        self.assertIn('endpoints', data)
        self.assertEqual(data['version'], '1.0.0')
        self.assertEqual(data['api'], 'v1')
    
    def test_health_check(self):
        """Test API health check endpoint."""
        response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['version'], '1.0.0')
    
    def test_register_user(self):
        """Test user registration via API."""
        response = self.client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'name': 'Test User'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertEqual(data['user']['email_address'], 'test@example.com')
        self.assertEqual(data['user']['name'], 'Test User')
    
    def test_register_duplicate_user(self):
        """Test registering duplicate user fails."""
        # Register first user
        self.client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'name': 'Test User'
            }),
            content_type='application/json'
        )
        
        # Try to register again
        response = self.client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'name': 'Another User'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_login(self):
        """Test user login via API."""
        # Register a user first
        self.client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'name': 'Test User'
            }),
            content_type='application/json'
        )
        
        # Login
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'email': 'test@example.com'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user fails."""
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'email': 'nonexistent@example.com'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_send_email(self):
        """Test sending email via API."""
        # Register two users
        response1 = self.client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                'email': 'sender@example.com',
                'name': 'Sender'
            }),
            content_type='application/json'
        )
        sender_token = json.loads(response1.data)['access_token']
        
        self.client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                'email': 'recipient@example.com',
                'name': 'Recipient'
            }),
            content_type='application/json'
        )
        
        # Send email
        response = self.client.post(
            '/api/v1/emails',
            data=json.dumps({
                'recipient': 'recipient@example.com',
                'subject': 'Test Email',
                'body': 'This is a test email'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {sender_token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['email']['sender'], 'sender@example.com')
        self.assertEqual(data['email']['recipient'], 'recipient@example.com')
    
    def test_send_email_without_token(self):
        """Test sending email without token fails."""
        response = self.client.post(
            '/api/v1/emails',
            data=json.dumps({
                'recipient': 'recipient@example.com',
                'subject': 'Test',
                'body': 'Body'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_get_inbox(self):
        """Test getting inbox via API."""
        # Register users
        response1 = self.client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                'email': 'sender@example.com',
                'name': 'Sender'
            }),
            content_type='application/json'
        )
        sender_token = json.loads(response1.data)['access_token']
        
        response2 = self.client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                'email': 'recipient@example.com',
                'name': 'Recipient'
            }),
            content_type='application/json'
        )
        recipient_token = json.loads(response2.data)['access_token']
        
        # Send email
        self.client.post(
            '/api/v1/emails',
            data=json.dumps({
                'recipient': 'recipient@example.com',
                'subject': 'Test Email',
                'body': 'This is a test'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {sender_token}'}
        )
        
        # Get inbox
        response = self.client.get(
            '/api/v1/emails/inbox',
            headers={'Authorization': f'Bearer {recipient_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['count'], 1)
        self.assertEqual(len(data['emails']), 1)
    
    def test_get_sent(self):
        """Test getting sent emails via API."""
        # Register users
        response1 = self.client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                'email': 'sender@example.com',
                'name': 'Sender'
            }),
            content_type='application/json'
        )
        sender_token = json.loads(response1.data)['access_token']
        
        self.client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                'email': 'recipient@example.com',
                'name': 'Recipient'
            }),
            content_type='application/json'
        )
        
        # Send email
        self.client.post(
            '/api/v1/emails',
            data=json.dumps({
                'recipient': 'recipient@example.com',
                'subject': 'Test Email',
                'body': 'This is a test'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {sender_token}'}
        )
        
        # Get sent emails
        response = self.client.get(
            '/api/v1/emails/sent',
            headers={'Authorization': f'Bearer {sender_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['count'], 1)
        self.assertEqual(len(data['emails']), 1)
    
    def test_refresh_token(self):
        """Test refreshing access token."""
        # Register user
        response = self.client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                'email': 'test@example.com',
                'name': 'Test User'
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        refresh_token = data['refresh_token']
        
        # Refresh access token
        response = self.client.post(
            '/api/v1/auth/refresh',
            data=json.dumps({
                'refresh_token': refresh_token
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('access_token', data)


if __name__ == "__main__":
    unittest.main()
