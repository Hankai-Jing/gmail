# Gmail-like Email System

A fully-functional Gmail-like system that allows users to send and receive emails. Built with Python, featuring both a command-line interface and a modern web UI with persistent database storage.

## Features

- **User Management**: Register and manage users with email addresses
- **Send Emails**: Send emails between registered users
- **Receive Emails**: View inbox with all received emails
- **Sent Folder**: View all sent emails
- **Read Emails**: Read individual emails and mark them as read
- **Email Tracking**: Automatic timestamping and unique ID generation
- **Database Persistence**: SQLite database for persistent storage
- **Web UI**: Modern, responsive web interface built with Flask
- **CLI Interface**: Traditional command-line interface for power users

## Architecture

The system is built with a clean, modular architecture:

- **models.py**: Data models for Email and User entities
- **storage.py**: In-memory storage layer for emails and users
- **database_storage.py**: SQLite-based persistent storage layer
- **email_service.py**: Business logic for email operations
- **app.py**: Flask web application with HTML templates
- **main.py**: Command-line interface for user interaction
- **demo.py**: Automated demo script
- **test_gmail.py**: Comprehensive unit tests for in-memory storage
- **test_database.py**: Unit tests for database storage

## Installation

### Option 1: CLI Only (No Dependencies)

For the command-line interface only, no external dependencies are required:

```bash
# Clone the repository
git clone https://github.com/Hankai-Jing/gmail.git
cd gmail

# Run the CLI application (requires Python 3.6+)
python main.py
```

### Option 2: Web UI (With Flask)

For the full web interface experience:

```bash
# Clone the repository
git clone https://github.com/Hankai-Jing/gmail.git
cd gmail

# Install dependencies
pip install -r requirements.txt

# Run the web application
python app.py
```

Then open your browser and navigate to `http://localhost:5000`

**Changing the Port:**

If port 5000 is already in use, you can specify a different port:

```bash
# Use port 8080 instead
FLASK_PORT=8080 python app.py

# Or with run_web.py
FLASK_PORT=8080 python run_web.py
```

## Usage

### Web Interface

Run the Flask web application:

```bash
python app.py
# Access at http://localhost:5000

# Or use a different port if 5000 is in use:
FLASK_PORT=8080 python app.py
# Access at http://localhost:8080
```

Features:
- **Home Page**: Welcome page with login/register options
- **Register**: Create a new user account
- **Login**: Access your account (simple email-based authentication)
- **Inbox**: View all received emails (unread emails are highlighted)
- **Sent**: View all sent emails
- **Compose**: Send new emails with recipient dropdown
- **View Email**: Read individual emails with full details
- **Users**: Browse all registered users

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

#### Using In-Memory Storage:

```python
from email_service import EmailService
from storage import EmailStorage

# Initialize the service with in-memory storage
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

#### Using Database Storage:

```python
from email_service import EmailService
from database_storage import DatabaseStorage

# Initialize the service with database storage
storage = DatabaseStorage('gmail.db')
service = EmailService(storage)

# Use the same API as above - data persists to SQLite database
service.register_user("alice@example.com", "Alice Smith")
# ... rest of the code is identical
```

## Running Tests

The system includes comprehensive unit tests covering all functionality:

```bash
# Run all in-memory storage tests (22 tests)
python -m unittest test_gmail.py -v

# Run all database storage tests (9 tests)
python -m unittest test_database.py -v

# Run all tests
python -m unittest discover -v

# Run specific test class
python -m unittest test_gmail.TestEmailService -v

# Run specific test
python -m unittest test_gmail.TestEmailService.test_send_email -v
```

All 31 tests should pass successfully.

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

1. **Dual Storage Options**: 
   - **In-Memory Storage**: Uses Python dictionaries for fast, simple storage perfect for testing and demos
   - **Database Storage**: SQLite-based persistent storage for production use with indexed queries

2. **User Registration Required**: Both sender and recipient must be registered before sending emails, providing a controlled environment.

3. **Read Status**: Only the recipient can mark an email as read, ensuring privacy.

4. **Sorting**: Emails in inbox and sent folders are sorted by timestamp (newest first) for easy browsing.

5. **UUID for Email IDs**: Uses UUID4 for globally unique email identifiers.

6. **Web UI with Flask**: Modern, responsive web interface using session-based authentication for simplicity.

## Implemented Features

- ✅ Database persistence (SQLite)
- ✅ Web-based UI (Flask)
- ✅ User management and authentication
- ✅ Email read/unread status tracking
- ✅ Inbox and sent folder organization
- ✅ Responsive design with visual feedback

## Future Enhancements

Possible improvements for a more complete system:
- Email threading/conversations
- Attachments support
- Search functionality
- Folders and labels
- Spam filtering
- Email encryption
- Real-time notifications (WebSocket)
- Multiple recipients (CC, BCC)
- Email drafts
- Delete and archive functionality
- Password-based authentication
- More advanced database (PostgreSQL, MongoDB)

## Technology Stack

- **Backend**: Python 3.6+
- **Web Framework**: Flask 3.0.0
- **Database**: SQLite3 (built-in)
- **Frontend**: HTML5, CSS3 (no JavaScript frameworks)
- **Testing**: unittest (Python standard library)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
