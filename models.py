"""
Data models for the Gmail-like system.
"""
from datetime import datetime
from typing import Optional
import uuid


class Email:
    """Represents an email message."""
    
    def __init__(
        self,
        sender: str,
        recipient: str,
        subject: str,
        body: str,
        email_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        read: bool = False
    ):
        """
        Initialize an email.
        
        Args:
            sender: Email address of the sender
            recipient: Email address of the recipient
            subject: Email subject line
            body: Email body content
            email_id: Unique identifier for the email (auto-generated if not provided)
            timestamp: Time when email was sent (auto-generated if not provided)
            read: Whether the email has been read
        """
        self.email_id = email_id or str(uuid.uuid4())
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.body = body
        self.timestamp = timestamp or datetime.now()
        self.read = read
    
    def mark_as_read(self):
        """Mark this email as read."""
        self.read = True
    
    def to_dict(self):
        """Convert email to dictionary representation."""
        return {
            'email_id': self.email_id,
            'sender': self.sender,
            'recipient': self.recipient,
            'subject': self.subject,
            'body': self.body,
            'timestamp': self.timestamp.isoformat(),
            'read': self.read
        }
    
    def __str__(self):
        """String representation of email."""
        status = "[Read]" if self.read else "[Unread]"
        return (f"{status} From: {self.sender}\n"
                f"To: {self.recipient}\n"
                f"Subject: {self.subject}\n"
                f"Date: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"ID: {self.email_id}\n"
                f"\n{self.body}")


class User:
    """Represents a user in the email system."""
    
    def __init__(self, email_address: str, name: str):
        """
        Initialize a user.
        
        Args:
            email_address: User's email address
            name: User's full name
        """
        self.email_address = email_address
        self.name = name
    
    def to_dict(self):
        """Convert user to dictionary representation."""
        return {
            'email_address': self.email_address,
            'name': self.name
        }
    
    def __str__(self):
        """String representation of user."""
        return f"{self.name} <{self.email_address}>"
