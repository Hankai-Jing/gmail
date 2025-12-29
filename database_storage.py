"""
Database storage layer using SQLite for persistence.
"""
import sqlite3
from datetime import datetime
from typing import List, Optional
from models import Email, User
from observability import LOGGER, METRICS, Timer, log_event


class DatabaseStorage:
    """SQLite-based persistent storage for emails and users."""
    
    def __init__(self, db_path: str = "gmail.db"):
        """
        Initialize the database storage.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema."""
        with Timer("db_operation_duration_seconds", labels={"operation": "init_database"}):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Create users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        email_address TEXT PRIMARY KEY,
                        name TEXT NOT NULL
                    )
                """)

                # Create emails table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS emails (
                        email_id TEXT PRIMARY KEY,
                        sender TEXT NOT NULL,
                        recipient TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        body TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        read INTEGER DEFAULT 0,
                        FOREIGN KEY (sender) REFERENCES users(email_address),
                        FOREIGN KEY (recipient) REFERENCES users(email_address)
                    )
                """)

                # Create indices for faster queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_emails_recipient 
                    ON emails(recipient, timestamp DESC)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_emails_sender 
                    ON emails(sender, timestamp DESC)
                """)

                conn.commit()
            except sqlite3.Error as exc:
                METRICS.inc_counter("db_errors_total", labels={"operation": "init_database"})
                log_event(
                    LOGGER,
                    "db.error",
                    operation="init_database",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                raise
            finally:
                if conn:
                    conn.close()
    
    def add_user(self, user: User) -> None:
        """
        Add a user to the database.
        
        Args:
            user: User to add
        """
        with Timer("db_operation_duration_seconds", labels={"operation": "add_user"}):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO users (email_address, name) VALUES (?, ?)",
                    (user.email_address, user.name)
                )

                conn.commit()
            except sqlite3.Error as exc:
                METRICS.inc_counter("db_errors_total", labels={"operation": "add_user"})
                log_event(
                    LOGGER,
                    "db.error",
                    operation="add_user",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                raise
            finally:
                if conn:
                    conn.close()
    
    def get_user(self, email_address: str) -> Optional[User]:
        """
        Get a user by email address.
        
        Args:
            email_address: Email address of the user
            
        Returns:
            User if found, None otherwise
        """
        with Timer("db_operation_duration_seconds", labels={"operation": "get_user"}):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT email_address, name FROM users WHERE email_address = ?",
                    (email_address,)
                )

                row = cursor.fetchone()
            except sqlite3.Error as exc:
                METRICS.inc_counter("db_errors_total", labels={"operation": "get_user"})
                log_event(
                    LOGGER,
                    "db.error",
                    operation="get_user",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                raise
            finally:
                if conn:
                    conn.close()
        
        if row:
            return User(email_address=row[0], name=row[1])
        return None
    
    def user_exists(self, email_address: str) -> bool:
        """
        Check if a user exists.
        
        Args:
            email_address: Email address to check
            
        Returns:
            True if user exists, False otherwise
        """
        with Timer("db_operation_duration_seconds", labels={"operation": "user_exists"}):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT COUNT(*) FROM users WHERE email_address = ?",
                    (email_address,)
                )

                count = cursor.fetchone()[0]
            except sqlite3.Error as exc:
                METRICS.inc_counter("db_errors_total", labels={"operation": "user_exists"})
                log_event(
                    LOGGER,
                    "db.error",
                    operation="user_exists",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                raise
            finally:
                if conn:
                    conn.close()
        
        return count > 0
    
    def store_email(self, email: Email) -> None:
        """
        Store an email in the database.
        
        Args:
            email: Email to store
        """
        with Timer("db_operation_duration_seconds", labels={"operation": "store_email"}):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """INSERT INTO emails 
                       (email_id, sender, recipient, subject, body, timestamp, read) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        email.email_id,
                        email.sender,
                        email.recipient,
                        email.subject,
                        email.body,
                        email.timestamp.isoformat(),
                        1 if email.read else 0
                    )
                )

                conn.commit()
            except sqlite3.Error as exc:
                METRICS.inc_counter("db_errors_total", labels={"operation": "store_email"})
                log_event(
                    LOGGER,
                    "db.error",
                    operation="store_email",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                raise
            finally:
                if conn:
                    conn.close()
    
    def get_email(self, email_id: str) -> Optional[Email]:
        """
        Get an email by ID.
        
        Args:
            email_id: ID of the email
            
        Returns:
            Email if found, None otherwise
        """
        with Timer("db_operation_duration_seconds", labels={"operation": "get_email"}):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """SELECT email_id, sender, recipient, subject, body, timestamp, read 
                       FROM emails WHERE email_id = ?""",
                    (email_id,)
                )

                row = cursor.fetchone()
            except sqlite3.Error as exc:
                METRICS.inc_counter("db_errors_total", labels={"operation": "get_email"})
                log_event(
                    LOGGER,
                    "db.error",
                    operation="get_email",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                raise
            finally:
                if conn:
                    conn.close()
        
        if row:
            return Email(
                email_id=row[0],
                sender=row[1],
                recipient=row[2],
                subject=row[3],
                body=row[4],
                timestamp=datetime.fromisoformat(row[5]),
                read=bool(row[6])
            )
        return None
    
    def update_email(self, email: Email) -> None:
        """
        Update an email in the database (e.g., to mark as read).
        
        Args:
            email: Email to update
        """
        with Timer("db_operation_duration_seconds", labels={"operation": "update_email"}):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """UPDATE emails SET read = ? WHERE email_id = ?""",
                    (1 if email.read else 0, email.email_id)
                )

                conn.commit()
            except sqlite3.Error as exc:
                METRICS.inc_counter("db_errors_total", labels={"operation": "update_email"})
                log_event(
                    LOGGER,
                    "db.error",
                    operation="update_email",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                raise
            finally:
                if conn:
                    conn.close()
    
    def get_inbox(self, email_address: str) -> List[Email]:
        """
        Get all emails for a recipient (inbox).
        
        Args:
            email_address: Email address of the recipient
            
        Returns:
            List of emails sent to this address, sorted by timestamp (newest first)
        """
        with Timer("db_operation_duration_seconds", labels={"operation": "get_inbox"}):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """SELECT email_id, sender, recipient, subject, body, timestamp, read 
                       FROM emails 
                       WHERE recipient = ? 
                       ORDER BY timestamp DESC""",
                    (email_address,)
                )

                rows = cursor.fetchall()
            except sqlite3.Error as exc:
                METRICS.inc_counter("db_errors_total", labels={"operation": "get_inbox"})
                log_event(
                    LOGGER,
                    "db.error",
                    operation="get_inbox",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                raise
            finally:
                if conn:
                    conn.close()
        
        emails = []
        for row in rows:
            emails.append(Email(
                email_id=row[0],
                sender=row[1],
                recipient=row[2],
                subject=row[3],
                body=row[4],
                timestamp=datetime.fromisoformat(row[5]),
                read=bool(row[6])
            ))
        
        return emails
    
    def get_sent(self, email_address: str) -> List[Email]:
        """
        Get all emails sent by a user.
        
        Args:
            email_address: Email address of the sender
            
        Returns:
            List of emails sent by this address, sorted by timestamp (newest first)
        """
        with Timer("db_operation_duration_seconds", labels={"operation": "get_sent"}):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """SELECT email_id, sender, recipient, subject, body, timestamp, read 
                       FROM emails 
                       WHERE sender = ? 
                       ORDER BY timestamp DESC""",
                    (email_address,)
                )

                rows = cursor.fetchall()
            except sqlite3.Error as exc:
                METRICS.inc_counter("db_errors_total", labels={"operation": "get_sent"})
                log_event(
                    LOGGER,
                    "db.error",
                    operation="get_sent",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                raise
            finally:
                if conn:
                    conn.close()
        
        emails = []
        for row in rows:
            emails.append(Email(
                email_id=row[0],
                sender=row[1],
                recipient=row[2],
                subject=row[3],
                body=row[4],
                timestamp=datetime.fromisoformat(row[5]),
                read=bool(row[6])
            ))
        
        return emails
    
    def get_all_users(self) -> List[User]:
        """
        Get all registered users.
        
        Returns:
            List of all users
        """
        with Timer("db_operation_duration_seconds", labels={"operation": "get_all_users"}):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT email_address, name FROM users")

                rows = cursor.fetchall()
            except sqlite3.Error as exc:
                METRICS.inc_counter("db_errors_total", labels={"operation": "get_all_users"})
                log_event(
                    LOGGER,
                    "db.error",
                    operation="get_all_users",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                raise
            finally:
                if conn:
                    conn.close()
        
        users = []
        for row in rows:
            users.append(User(email_address=row[0], name=row[1]))
        
        return users
    
    def clear(self) -> None:
        """Clear all emails and users (useful for testing)."""
        with Timer("db_operation_duration_seconds", labels={"operation": "clear"}):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("DELETE FROM emails")
                cursor.execute("DELETE FROM users")

                conn.commit()
            except sqlite3.Error as exc:
                METRICS.inc_counter("db_errors_total", labels={"operation": "clear"})
                log_event(
                    LOGGER,
                    "db.error",
                    operation="clear",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                raise
            finally:
                if conn:
                    conn.close()

    def health_check(self) -> bool:
        """Check database connectivity."""
        with Timer("db_operation_duration_seconds", labels={"operation": "health_check"}):
            conn = None
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                return True
            except sqlite3.Error as exc:
                METRICS.inc_counter("db_errors_total", labels={"operation": "health_check"})
                log_event(
                    LOGGER,
                    "db.error",
                    operation="health_check",
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
                return False
            finally:
                if conn:
                    conn.close()
