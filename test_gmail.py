"""
Unit tests for the Gmail-like system.
"""
import unittest
from datetime import datetime
from models import Email, User
from storage import EmailStorage
from email_service import EmailService


class TestEmail(unittest.TestCase):
    """Test cases for Email model."""
    
    def test_email_creation(self):
        """Test creating an email."""
        email = Email(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        self.assertEqual(email.sender, "sender@example.com")
        self.assertEqual(email.recipient, "recipient@example.com")
        self.assertEqual(email.subject, "Test Subject")
        self.assertEqual(email.body, "Test Body")
        self.assertFalse(email.read)
        self.assertIsNotNone(email.email_id)
        self.assertIsInstance(email.timestamp, datetime)
    
    def test_mark_as_read(self):
        """Test marking an email as read."""
        email = Email(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Test",
            body="Test"
        )
        
        self.assertFalse(email.read)
        email.mark_as_read()
        self.assertTrue(email.read)
    
    def test_email_to_dict(self):
        """Test converting email to dictionary."""
        email = Email(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Test",
            body="Test"
        )
        
        data = email.to_dict()
        self.assertEqual(data['sender'], "sender@example.com")
        self.assertEqual(data['recipient'], "recipient@example.com")
        self.assertEqual(data['subject'], "Test")
        self.assertEqual(data['body'], "Test")
        self.assertFalse(data['read'])


class TestUser(unittest.TestCase):
    """Test cases for User model."""
    
    def test_user_creation(self):
        """Test creating a user."""
        user = User("user@example.com", "John Doe")
        
        self.assertEqual(user.email_address, "user@example.com")
        self.assertEqual(user.name, "John Doe")
    
    def test_user_to_dict(self):
        """Test converting user to dictionary."""
        user = User("user@example.com", "John Doe")
        
        data = user.to_dict()
        self.assertEqual(data['email_address'], "user@example.com")
        self.assertEqual(data['name'], "John Doe")


class TestEmailStorage(unittest.TestCase):
    """Test cases for EmailStorage."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.storage = EmailStorage()
    
    def test_add_and_get_user(self):
        """Test adding and retrieving a user."""
        user = User("user@example.com", "John Doe")
        self.storage.add_user(user)
        
        retrieved = self.storage.get_user("user@example.com")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.email_address, "user@example.com")
        self.assertEqual(retrieved.name, "John Doe")
    
    def test_user_exists(self):
        """Test checking if user exists."""
        user = User("user@example.com", "John Doe")
        self.storage.add_user(user)
        
        self.assertTrue(self.storage.user_exists("user@example.com"))
        self.assertFalse(self.storage.user_exists("other@example.com"))
    
    def test_store_and_get_email(self):
        """Test storing and retrieving an email."""
        email = Email(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Test",
            body="Test"
        )
        self.storage.store_email(email)
        
        retrieved = self.storage.get_email(email.email_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.email_id, email.email_id)
        self.assertEqual(retrieved.sender, "sender@example.com")
    
    def test_get_inbox(self):
        """Test getting inbox emails."""
        # Create emails
        email1 = Email("sender1@example.com", "user@example.com", "Subject 1", "Body 1")
        email2 = Email("sender2@example.com", "user@example.com", "Subject 2", "Body 2")
        email3 = Email("sender1@example.com", "other@example.com", "Subject 3", "Body 3")
        
        self.storage.store_email(email1)
        self.storage.store_email(email2)
        self.storage.store_email(email3)
        
        # Get inbox for user@example.com
        inbox = self.storage.get_inbox("user@example.com")
        self.assertEqual(len(inbox), 2)
        self.assertIn(email1, inbox)
        self.assertIn(email2, inbox)
        self.assertNotIn(email3, inbox)
    
    def test_get_sent(self):
        """Test getting sent emails."""
        # Create emails
        email1 = Email("user@example.com", "recipient1@example.com", "Subject 1", "Body 1")
        email2 = Email("user@example.com", "recipient2@example.com", "Subject 2", "Body 2")
        email3 = Email("other@example.com", "recipient1@example.com", "Subject 3", "Body 3")
        
        self.storage.store_email(email1)
        self.storage.store_email(email2)
        self.storage.store_email(email3)
        
        # Get sent emails for user@example.com
        sent = self.storage.get_sent("user@example.com")
        self.assertEqual(len(sent), 2)
        self.assertIn(email1, sent)
        self.assertIn(email2, sent)
        self.assertNotIn(email3, sent)
    
    def test_clear(self):
        """Test clearing storage."""
        user = User("user@example.com", "John Doe")
        email = Email("sender@example.com", "recipient@example.com", "Test", "Test")
        
        self.storage.add_user(user)
        self.storage.store_email(email)
        
        self.storage.clear()
        
        self.assertFalse(self.storage.user_exists("user@example.com"))
        self.assertIsNone(self.storage.get_email(email.email_id))


class TestEmailService(unittest.TestCase):
    """Test cases for EmailService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.storage = EmailStorage()
        self.service = EmailService(self.storage)
    
    def test_register_user(self):
        """Test registering a user."""
        user = self.service.register_user("user@example.com", "John Doe")
        
        self.assertEqual(user.email_address, "user@example.com")
        self.assertEqual(user.name, "John Doe")
        self.assertTrue(self.storage.user_exists("user@example.com"))
    
    def test_register_duplicate_user(self):
        """Test registering a duplicate user raises error."""
        self.service.register_user("user@example.com", "John Doe")
        
        with self.assertRaises(ValueError):
            self.service.register_user("user@example.com", "Jane Doe")
    
    def test_send_email(self):
        """Test sending an email."""
        # Register users
        self.service.register_user("sender@example.com", "Sender")
        self.service.register_user("recipient@example.com", "Recipient")
        
        # Send email
        email = self.service.send_email(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        self.assertEqual(email.sender, "sender@example.com")
        self.assertEqual(email.recipient, "recipient@example.com")
        self.assertEqual(email.subject, "Test Subject")
        self.assertEqual(email.body, "Test Body")
    
    def test_send_email_unregistered_sender(self):
        """Test sending email from unregistered sender raises error."""
        self.service.register_user("recipient@example.com", "Recipient")
        
        with self.assertRaises(ValueError):
            self.service.send_email(
                sender="unregistered@example.com",
                recipient="recipient@example.com",
                subject="Test",
                body="Test"
            )
    
    def test_send_email_unregistered_recipient(self):
        """Test sending email to unregistered recipient raises error."""
        self.service.register_user("sender@example.com", "Sender")
        
        with self.assertRaises(ValueError):
            self.service.send_email(
                sender="sender@example.com",
                recipient="unregistered@example.com",
                subject="Test",
                body="Test"
            )
    
    def test_get_inbox(self):
        """Test getting inbox."""
        # Register users
        self.service.register_user("sender@example.com", "Sender")
        self.service.register_user("recipient@example.com", "Recipient")
        
        # Send emails
        self.service.send_email("sender@example.com", "recipient@example.com", "Test 1", "Body 1")
        self.service.send_email("sender@example.com", "recipient@example.com", "Test 2", "Body 2")
        
        # Get inbox
        inbox = self.service.get_inbox("recipient@example.com")
        self.assertEqual(len(inbox), 2)
    
    def test_get_inbox_unregistered_user(self):
        """Test getting inbox for unregistered user raises error."""
        with self.assertRaises(ValueError):
            self.service.get_inbox("unregistered@example.com")
    
    def test_get_sent(self):
        """Test getting sent emails."""
        # Register users
        self.service.register_user("sender@example.com", "Sender")
        self.service.register_user("recipient@example.com", "Recipient")
        
        # Send emails
        self.service.send_email("sender@example.com", "recipient@example.com", "Test 1", "Body 1")
        self.service.send_email("sender@example.com", "recipient@example.com", "Test 2", "Body 2")
        
        # Get sent emails
        sent = self.service.get_sent("sender@example.com")
        self.assertEqual(len(sent), 2)
    
    def test_read_email(self):
        """Test reading an email."""
        # Register users
        self.service.register_user("sender@example.com", "Sender")
        self.service.register_user("recipient@example.com", "Recipient")
        
        # Send email
        email = self.service.send_email(
            "sender@example.com",
            "recipient@example.com",
            "Test",
            "Body"
        )
        
        # Read email
        read_email = self.service.read_email(email.email_id, "recipient@example.com")
        self.assertIsNotNone(read_email)
        self.assertTrue(read_email.read)
    
    def test_read_email_unauthorized(self):
        """Test reading email by non-recipient raises error."""
        # Register users
        self.service.register_user("sender@example.com", "Sender")
        self.service.register_user("recipient@example.com", "Recipient")
        self.service.register_user("other@example.com", "Other")
        
        # Send email
        email = self.service.send_email(
            "sender@example.com",
            "recipient@example.com",
            "Test",
            "Body"
        )
        
        # Try to read as non-recipient
        with self.assertRaises(ValueError):
            self.service.read_email(email.email_id, "other@example.com")
    
    def test_list_users(self):
        """Test listing all users."""
        self.service.register_user("user1@example.com", "User 1")
        self.service.register_user("user2@example.com", "User 2")
        
        users = self.service.list_users()
        self.assertEqual(len(users), 2)


if __name__ == "__main__":
    unittest.main()
