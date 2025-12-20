# Gmail-like Email System

A simple, fully-functional Gmail-like system that allows users to send and receive emails. Built with Python using only the standard library.

## Features

- **User Management**: Register and manage users with email addresses
- **Send Emails**: Send emails between registered users
- **Receive Emails**: View inbox with all received emails
- **Sent Folder**: View all sent emails
- **Read Emails**: Read individual emails and mark them as read
- **Email Tracking**: Automatic timestamping and unique ID generation
- **In-Memory Storage**: Fast, lightweight storage for development and testing

## Architecture

The system is built with a clean, modular architecture:

- **models.py**: Data models for Email and User entities
- **storage.py**: In-memory storage layer for emails and users
- **email_service.py**: Business logic for email operations
- **main.py**: Command-line interface for user interaction
- **test_gmail.py**: Comprehensive unit tests

## Installation

No external dependencies required! The system uses only Python's standard library.

```bash
# Clone the repository
git clone https://github.com/Hankai-Jing/gmail.git
cd gmail

# Run the application (requires Python 3.6+)
python main.py
```

## Usage

### Interactive CLI

Run the main application to use the interactive command-line interface:

```bash
python main.py
```

The CLI provides the following options:
1. **Register a user**: Create a new user account
2. **Send an email**: Send an email from one user to another
3. **View inbox**: See all received emails
4. **View sent emails**: See all emails you've sent
5. **Read an email**: Read a specific email by ID and mark it as read
6. **List all users**: View all registered users
7. **Exit**: Close the application

### Programmatic Usage

You can also use the system programmatically in your Python code:

```python
from email_service import EmailService
from storage import EmailStorage

# Initialize the service
storage = EmailStorage()
service = EmailService(storage)

# Register users
service.register_user("alice@example.com", "Alice Smith")
service.register_user("bob@example.com", "Bob Jones")

# Send an email
email = service.send_email(
    sender="alice@example.com",
    recipient="bob@example.com",
    subject="Hello!",
    body="This is a test email."
)

# Get inbox
inbox = service.get_inbox("bob@example.com")
print(f"Bob has {len(inbox)} email(s)")

# Read an email
read_email = service.read_email(email.email_id, "bob@example.com")
print(read_email)
```

## Running Tests

The system includes comprehensive unit tests covering all functionality:

```bash
# Run all tests
python -m unittest test_gmail.py -v

# Run specific test class
python -m unittest test_gmail.TestEmailService -v

# Run specific test
python -m unittest test_gmail.TestEmailService.test_send_email -v
```

All 22 tests should pass successfully.

## API Reference

### EmailService

- `register_user(email_address, name)`: Register a new user
- `send_email(sender, recipient, subject, body)`: Send an email
- `get_inbox(email_address)`: Get all emails received by a user
- `get_sent(email_address)`: Get all emails sent by a user
- `read_email(email_id, user_email)`: Read and mark an email as read
- `list_users()`: Get all registered users

### Email Model

- `email_id`: Unique identifier (auto-generated UUID)
- `sender`: Sender's email address
- `recipient`: Recipient's email address
- `subject`: Email subject line
- `body`: Email body content
- `timestamp`: When the email was sent (auto-generated)
- `read`: Whether the email has been read (default: False)
- `mark_as_read()`: Mark the email as read

### User Model

- `email_address`: User's email address (unique identifier)
- `name`: User's full name

## Example Session

```
Welcome to the Gmail-like System!

=== Gmail-like System ===
1. Register a user
2. Send an email
3. View inbox
4. View sent emails
5. Read an email
6. List all users
7. Exit
========================

Enter your choice (1-7): 1

--- Register User ---
Enter email address: alice@example.com
Enter full name: Alice Smith
✓ User registered successfully: Alice Smith <alice@example.com>

Enter your choice (1-7): 1

--- Register User ---
Enter email address: bob@example.com
Enter full name: Bob Jones
✓ User registered successfully: Bob Jones <bob@example.com>

Enter your choice (1-7): 2

--- Send Email ---
From (email): alice@example.com
To (email): bob@example.com
Subject: Meeting Tomorrow
Body (press Enter twice to finish):
Hi Bob,
Just a reminder about our meeting tomorrow at 10 AM.

✓ Email sent successfully! ID: 12345678-1234-1234-1234-123456789abc

Enter your choice (1-7): 3

--- View Inbox ---
Enter your email address: bob@example.com

1 email(s) in inbox:
--------------------------------------------------------------------------------
1. ✗ From: alice@example.com
   Subject: Meeting Tomorrow
   Date: 2025-12-20 21:13:00
   ID: 12345678-1234-1234-1234-123456789abc
--------------------------------------------------------------------------------
```

## Design Decisions

1. **In-Memory Storage**: Uses Python dictionaries for fast, simple storage. For production use, this could be replaced with a database backend.

2. **User Registration Required**: Both sender and recipient must be registered before sending emails, providing a controlled environment.

3. **Read Status**: Only the recipient can mark an email as read, ensuring privacy.

4. **Sorting**: Emails in inbox and sent folders are sorted by timestamp (newest first) for easy browsing.

5. **UUID for Email IDs**: Uses UUID4 for globally unique email identifiers.

## Future Enhancements

Possible improvements for a production system:
- Database persistence (PostgreSQL, MongoDB, etc.)
- Email threading/conversations
- Attachments support
- Search functionality
- Folders and labels
- Spam filtering
- Email encryption
- Web-based UI
- Real-time notifications
- Multiple recipients (CC, BCC)
- Email drafts
- Delete and archive functionality

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
