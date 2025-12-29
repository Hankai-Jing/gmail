"""
Email service for sending and receiving emails.
"""
from typing import List, Optional
from observability import LOGGER, METRICS, Timer, get_request_id, hash_email, log_event
from models import Email, User
from storage import EmailStorage


class EmailService:
    """Service for managing email operations."""
    
    def __init__(self, storage: EmailStorage):
        """
        Initialize the email service.
        
        Args:
            storage: Email storage instance
        """
        self.storage = storage
    
    def register_user(self, email_address: str, name: str) -> User:
        """
        Register a new user.
        
        Args:
            email_address: User's email address
            name: User's full name
            
        Returns:
            The created User object
            
        Raises:
            ValueError: If user already exists
        """
        with Timer("email_service_duration_seconds", labels={"operation": "register_user"}):
            if self.storage.user_exists(email_address):
                METRICS.inc_counter(
                    "user_register_total",
                    labels={"status": "error", "reason": "exists"},
                )
                log_event(
                    LOGGER,
                    "user.register",
                    request_id=get_request_id(),
                    status="error",
                    reason="exists",
                    user_hash=hash_email(email_address),
                )
                raise ValueError(f"User with email {email_address} already exists")
        
        user = User(email_address, name)
        self.storage.add_user(user)
        METRICS.inc_counter("user_register_total", labels={"status": "success"})
        log_event(
            LOGGER,
            "user.register",
            request_id=get_request_id(),
            status="success",
            user_hash=hash_email(email_address),
        )
        return user
    
    def send_email(
        self,
        sender: str,
        recipient: str,
        subject: str,
        body: str
    ) -> Email:
        """
        Send an email from sender to recipient.
        
        Args:
            sender: Email address of the sender
            recipient: Email address of the recipient
            subject: Email subject
            body: Email body content
            
        Returns:
            The sent Email object
            
        Raises:
            ValueError: If sender or recipient doesn't exist
        """
        with Timer("email_service_duration_seconds", labels={"operation": "send_email"}):
            # Validate sender exists
            if not self.storage.user_exists(sender):
                METRICS.inc_counter("emails_sent_total", labels={"status": "error", "reason": "sender_missing"})
                log_event(
                    LOGGER,
                    "email.send",
                    request_id=get_request_id(),
                    status="error",
                    reason="sender_missing",
                    sender_hash=hash_email(sender),
                )
                raise ValueError(f"Sender {sender} is not registered")

            # Validate recipient exists
            if not self.storage.user_exists(recipient):
                METRICS.inc_counter("emails_sent_total", labels={"status": "error", "reason": "recipient_missing"})
                log_event(
                    LOGGER,
                    "email.send",
                    request_id=get_request_id(),
                    status="error",
                    reason="recipient_missing",
                    sender_hash=hash_email(sender),
                    recipient_hash=hash_email(recipient),
                )
                raise ValueError(f"Recipient {recipient} is not registered")

            # Create and store the email
            email = Email(
                sender=sender,
                recipient=recipient,
                subject=subject,
                body=body
            )
            self.storage.store_email(email)
            METRICS.inc_counter("emails_sent_total", labels={"status": "success"})
            log_event(
                LOGGER,
                "email.send",
                request_id=get_request_id(),
                status="success",
                sender_hash=hash_email(sender),
                recipient_hash=hash_email(recipient),
                email_id=email.email_id,
            )
            return email
    
    def get_inbox(self, email_address: str) -> List[Email]:
        """
        Get all emails in a user's inbox.
        
        Args:
            email_address: Email address of the user
            
        Returns:
            List of emails in the inbox (received emails)
            
        Raises:
            ValueError: If user doesn't exist
        """
        with Timer("email_service_duration_seconds", labels={"operation": "get_inbox"}):
            if not self.storage.user_exists(email_address):
                METRICS.inc_counter("emails_inbox_total", labels={"status": "error", "reason": "user_missing"})
                log_event(
                    LOGGER,
                    "email.inbox",
                    request_id=get_request_id(),
                    status="error",
                    reason="user_missing",
                    user_hash=hash_email(email_address),
                )
                raise ValueError(f"User {email_address} is not registered")

            emails = self.storage.get_inbox(email_address)
            METRICS.inc_counter("emails_inbox_total", labels={"status": "success"})
            log_event(
                LOGGER,
                "email.inbox",
                request_id=get_request_id(),
                status="success",
                user_hash=hash_email(email_address),
                count=len(emails),
            )
            return emails
    
    def get_sent(self, email_address: str) -> List[Email]:
        """
        Get all emails sent by a user.
        
        Args:
            email_address: Email address of the user
            
        Returns:
            List of emails sent by the user
            
        Raises:
            ValueError: If user doesn't exist
        """
        with Timer("email_service_duration_seconds", labels={"operation": "get_sent"}):
            if not self.storage.user_exists(email_address):
                METRICS.inc_counter("emails_sent_list_total", labels={"status": "error", "reason": "user_missing"})
                log_event(
                    LOGGER,
                    "email.sent",
                    request_id=get_request_id(),
                    status="error",
                    reason="user_missing",
                    user_hash=hash_email(email_address),
                )
                raise ValueError(f"User {email_address} is not registered")

            emails = self.storage.get_sent(email_address)
            METRICS.inc_counter("emails_sent_list_total", labels={"status": "success"})
            log_event(
                LOGGER,
                "email.sent",
                request_id=get_request_id(),
                status="success",
                user_hash=hash_email(email_address),
                count=len(emails),
            )
            return emails
    
    def read_email(self, email_id: str, user_email: str) -> Optional[Email]:
        """
        Read an email and mark it as read.
        
        Args:
            email_id: ID of the email to read
            user_email: Email address of the user reading the email
            
        Returns:
            The email if found and user is authorized, None otherwise
            
        Raises:
            ValueError: If user is not the recipient
        """
        with Timer("email_service_duration_seconds", labels={"operation": "read_email"}):
            email = self.storage.get_email(email_id)

            if not email:
                METRICS.inc_counter("emails_read_total", labels={"status": "not_found"})
                log_event(
                    LOGGER,
                    "email.read",
                    request_id=get_request_id(),
                    status="not_found",
                    email_id=email_id,
                )
                return None

            # Only the recipient can read/mark as read
            if email.recipient != user_email:
                METRICS.inc_counter("emails_read_total", labels={"status": "unauthorized"})
                log_event(
                    LOGGER,
                    "email.read",
                    request_id=get_request_id(),
                    status="unauthorized",
                    email_id=email_id,
                    user_hash=hash_email(user_email),
                )
                raise ValueError(f"User {user_email} is not authorized to read this email")

            email.mark_as_read()

            # Persist the read status if storage supports it
            if hasattr(self.storage, 'update_email'):
                self.storage.update_email(email)

            METRICS.inc_counter("emails_read_total", labels={"status": "success"})
            log_event(
                LOGGER,
                "email.read",
                request_id=get_request_id(),
                status="success",
                email_id=email_id,
                user_hash=hash_email(user_email),
            )
            return email
    
    def get_user(self, email_address: str) -> Optional[User]:
        """
        Get a user by email address.
        
        Args:
            email_address: Email address of the user
            
        Returns:
            User if found, None otherwise
        """
        return self.storage.get_user(email_address)
    
    def list_users(self) -> List[User]:
        """
        Get all registered users.
        
        Returns:
            List of all users
        """
        return self.storage.get_all_users()
