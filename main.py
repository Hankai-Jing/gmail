#!/usr/bin/env python3
"""
Command-line interface for the Gmail-like system.
"""
import sys
from email_service import EmailService
from storage import EmailStorage


def print_menu():
    """Print the main menu."""
    print("\n=== Gmail-like System ===")
    print("1. Register a user")
    print("2. Send an email")
    print("3. View inbox")
    print("4. View sent emails")
    print("5. Read an email")
    print("6. List all users")
    print("7. Exit")
    print("========================")


def register_user(service: EmailService):
    """Register a new user."""
    print("\n--- Register User ---")
    email = input("Enter email address: ").strip()
    name = input("Enter full name: ").strip()
    
    try:
        user = service.register_user(email, name)
        print(f"✓ User registered successfully: {user}")
    except ValueError as e:
        print(f"✗ Error: {e}")


def send_email(service: EmailService):
    """Send an email."""
    print("\n--- Send Email ---")
    sender = input("From (email): ").strip()
    recipient = input("To (email): ").strip()
    subject = input("Subject: ").strip()
    print("Body (press Enter twice to finish):")
    
    body_lines = []
    empty_line_count = 0
    while empty_line_count < 2:
        line = input()
        if line == "":
            empty_line_count += 1
        else:
            empty_line_count = 0
            body_lines.append(line)
    
    body = "\n".join(body_lines)
    
    try:
        email = service.send_email(sender, recipient, subject, body)
        print(f"✓ Email sent successfully! ID: {email.email_id}")
    except ValueError as e:
        print(f"✗ Error: {e}")


def view_inbox(service: EmailService):
    """View a user's inbox."""
    print("\n--- View Inbox ---")
    email = input("Enter your email address: ").strip()
    
    try:
        inbox = service.get_inbox(email)
        if not inbox:
            print("Inbox is empty.")
        else:
            print(f"\n{len(inbox)} email(s) in inbox:")
            print("-" * 80)
            for i, email_obj in enumerate(inbox, 1):
                status = "✓" if email_obj.read else "✗"
                print(f"{i}. {status} From: {email_obj.sender}")
                print(f"   Subject: {email_obj.subject}")
                print(f"   Date: {email_obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   ID: {email_obj.email_id}")
                print("-" * 80)
    except ValueError as e:
        print(f"✗ Error: {e}")


def view_sent(service: EmailService):
    """View a user's sent emails."""
    print("\n--- View Sent Emails ---")
    email = input("Enter your email address: ").strip()
    
    try:
        sent = service.get_sent(email)
        if not sent:
            print("No sent emails.")
        else:
            print(f"\n{len(sent)} sent email(s):")
            print("-" * 80)
            for i, email_obj in enumerate(sent, 1):
                print(f"{i}. To: {email_obj.recipient}")
                print(f"   Subject: {email_obj.subject}")
                print(f"   Date: {email_obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   ID: {email_obj.email_id}")
                print("-" * 80)
    except ValueError as e:
        print(f"✗ Error: {e}")


def read_email(service: EmailService):
    """Read a specific email."""
    print("\n--- Read Email ---")
    user_email = input("Enter your email address: ").strip()
    email_id = input("Enter email ID: ").strip()
    
    try:
        email = service.read_email(email_id, user_email)
        if email:
            print("\n" + "=" * 80)
            print(email)
            print("=" * 80)
        else:
            print("✗ Email not found.")
    except ValueError as e:
        print(f"✗ Error: {e}")


def list_users(service: EmailService):
    """List all registered users."""
    print("\n--- Registered Users ---")
    users = service.list_users()
    
    if not users:
        print("No users registered.")
    else:
        print(f"\n{len(users)} registered user(s):")
        for i, user in enumerate(users, 1):
            print(f"{i}. {user}")


def main():
    """Main function."""
    # Initialize the email service
    storage = EmailStorage()
    service = EmailService(storage)
    
    print("Welcome to the Gmail-like System!")
    print("This is a demonstration of email sending and receiving functionality.")
    
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            register_user(service)
        elif choice == "2":
            send_email(service)
        elif choice == "3":
            view_inbox(service)
        elif choice == "4":
            view_sent(service)
        elif choice == "5":
            read_email(service)
        elif choice == "6":
            list_users(service)
        elif choice == "7":
            print("\nGoodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
