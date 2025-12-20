"""
Storage layer for emails and users.
This provides in-memory storage for the Gmail-like system.
"""
from typing import List, Optional, Dict
from models import Email, User


class EmailStorage:
    """In-memory storage for emails."""
    
    def __init__(self):
        """Initialize the email storage."""
        self._emails: Dict[str, Email] = {}  # email_id -> Email
        self._users: Dict[str, User] = {}    # email_address -> User
    
    def add_user(self, user: User) -> None:
        """
        Add a user to the system.
        
        Args:
            user: User to add
        """
        self._users[user.email_address] = user
    
    def get_user(self, email_address: str) -> Optional[User]:
        """
        Get a user by email address.
        
        Args:
            email_address: Email address of the user
            
        Returns:
            User if found, None otherwise
        """
        return self._users.get(email_address)
    
    def user_exists(self, email_address: str) -> bool:
        """
        Check if a user exists.
        
        Args:
            email_address: Email address to check
            
        Returns:
            True if user exists, False otherwise
        """
        return email_address in self._users
    
    def store_email(self, email: Email) -> None:
        """
        Store an email.
        
        Args:
            email: Email to store
        """
        self._emails[email.email_id] = email
    
    def get_email(self, email_id: str) -> Optional[Email]:
        """
        Get an email by ID.
        
        Args:
            email_id: ID of the email
            
        Returns:
            Email if found, None otherwise
        """
        return self._emails.get(email_id)
    
    def get_inbox(self, email_address: str) -> List[Email]:
        """
        Get all emails for a recipient (inbox).
        
        Args:
            email_address: Email address of the recipient
            
        Returns:
            List of emails sent to this address, sorted by timestamp (newest first)
        """
        inbox = [
            email for email in self._emails.values()
            if email.recipient == email_address
        ]
        # Sort by timestamp, newest first
        inbox.sort(key=lambda e: e.timestamp, reverse=True)
        return inbox
    
    def get_sent(self, email_address: str) -> List[Email]:
        """
        Get all emails sent by a user.
        
        Args:
            email_address: Email address of the sender
            
        Returns:
            List of emails sent by this address, sorted by timestamp (newest first)
        """
        sent = [
            email for email in self._emails.values()
            if email.sender == email_address
        ]
        # Sort by timestamp, newest first
        sent.sort(key=lambda e: e.timestamp, reverse=True)
        return sent
    
    def get_all_users(self) -> List[User]:
        """
        Get all registered users.
        
        Returns:
            List of all users
        """
        return list(self._users.values())
    
    def clear(self) -> None:
        """Clear all emails and users (useful for testing)."""
        self._emails.clear()
        self._users.clear()
