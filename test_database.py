"""
Unit tests for database storage.
"""
import unittest
import os
from datetime import datetime
from models import Email, User
from database_storage import DatabaseStorage


class TestDatabaseStorage(unittest.TestCase):
    """Test cases for DatabaseStorage."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_db = "test_gmail.db"
        self.storage = DatabaseStorage(self.test_db)
    
    def tearDown(self):
        """Clean up after tests."""
        self.storage.clear()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
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
    
    def test_update_email(self):
        """Test updating an email (mark as read)."""
        email = Email(
            sender="sender@example.com",
            recipient="recipient@example.com",
            subject="Test",
            body="Test"
        )
        self.storage.store_email(email)
        
        # Mark as read and update
        email.mark_as_read()
        self.storage.update_email(email)
        
        # Retrieve and verify
        retrieved = self.storage.get_email(email.email_id)
        self.assertTrue(retrieved.read)
    
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
        
        # Check that emails are sorted by timestamp (newest first)
        self.assertEqual(inbox[0].subject, "Subject 2")
        self.assertEqual(inbox[1].subject, "Subject 1")
    
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
        
        # Check that emails are sorted by timestamp (newest first)
        self.assertEqual(sent[0].subject, "Subject 2")
        self.assertEqual(sent[1].subject, "Subject 1")
    
    def test_get_all_users(self):
        """Test getting all users."""
        user1 = User("user1@example.com", "User 1")
        user2 = User("user2@example.com", "User 2")
        
        self.storage.add_user(user1)
        self.storage.add_user(user2)
        
        users = self.storage.get_all_users()
        self.assertEqual(len(users), 2)
    
    def test_clear(self):
        """Test clearing storage."""
        user = User("user@example.com", "John Doe")
        email = Email("sender@example.com", "recipient@example.com", "Test", "Test")
        
        self.storage.add_user(user)
        self.storage.store_email(email)
        
        self.storage.clear()
        
        self.assertFalse(self.storage.user_exists("user@example.com"))
        self.assertIsNone(self.storage.get_email(email.email_id))
    
    def test_persistence(self):
        """Test that data persists across storage instances."""
        user = User("user@example.com", "John Doe")
        email = Email("sender@example.com", "user@example.com", "Test", "Body")
        
        self.storage.add_user(user)
        self.storage.store_email(email)
        
        # Create new storage instance with same database
        storage2 = DatabaseStorage(self.test_db)
        
        # Verify data persisted
        self.assertTrue(storage2.user_exists("user@example.com"))
        retrieved_email = storage2.get_email(email.email_id)
        self.assertIsNotNone(retrieved_email)
        self.assertEqual(retrieved_email.subject, "Test")


if __name__ == "__main__":
    unittest.main()
