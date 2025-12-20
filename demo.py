#!/usr/bin/env python3
"""
Quick demonstration of the Gmail-like system functionality.
"""
from email_service import EmailService
from storage import EmailStorage


def main():
    """Run a quick demonstration."""
    print("=" * 80)
    print("Gmail-like System - Quick Demo")
    print("=" * 80)
    
    # Initialize the service
    storage = EmailStorage()
    service = EmailService(storage)
    
    print("\n1. Registering users...")
    alice = service.register_user("alice@example.com", "Alice Smith")
    bob = service.register_user("bob@example.com", "Bob Jones")
    charlie = service.register_user("charlie@example.com", "Charlie Brown")
    print(f"   ✓ Registered: {alice}")
    print(f"   ✓ Registered: {bob}")
    print(f"   ✓ Registered: {charlie}")
    
    print("\n2. Sending emails...")
    email1 = service.send_email(
        sender="alice@example.com",
        recipient="bob@example.com",
        subject="Project Update",
        body="Hi Bob,\n\nThe project is progressing well. Let's meet tomorrow to discuss next steps.\n\nBest,\nAlice"
    )
    print(f"   ✓ Email sent from Alice to Bob (ID: {email1.email_id[:8]}...)")
    
    email2 = service.send_email(
        sender="charlie@example.com",
        recipient="bob@example.com",
        subject="Lunch Plans",
        body="Hey Bob,\n\nWant to grab lunch today at noon?\n\nCharlie"
    )
    print(f"   ✓ Email sent from Charlie to Bob (ID: {email2.email_id[:8]}...)")
    
    email3 = service.send_email(
        sender="bob@example.com",
        recipient="alice@example.com",
        subject="RE: Project Update",
        body="Hi Alice,\n\nSounds good! How about 2 PM in the conference room?\n\nBob"
    )
    print(f"   ✓ Email sent from Bob to Alice (ID: {email3.email_id[:8]}...)")
    
    print("\n3. Viewing Bob's inbox...")
    bob_inbox = service.get_inbox("bob@example.com")
    print(f"   Bob has {len(bob_inbox)} email(s) in his inbox:")
    for i, email in enumerate(bob_inbox, 1):
        status = "[Read]" if email.read else "[Unread]"
        print(f"   {i}. {status} From: {email.sender}")
        print(f"      Subject: {email.subject}")
        print(f"      Date: {email.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n4. Bob reads the first email...")
    read_email = service.read_email(bob_inbox[0].email_id, "bob@example.com")
    print(f"   ✓ Bob read email from {read_email.sender}")
    print(f"   Subject: {read_email.subject}")
    print(f"   Status: {'Read' if read_email.read else 'Unread'}")
    
    print("\n5. Viewing Bob's sent emails...")
    bob_sent = service.get_sent("bob@example.com")
    print(f"   Bob has sent {len(bob_sent)} email(s):")
    for i, email in enumerate(bob_sent, 1):
        print(f"   {i}. To: {email.recipient}")
        print(f"      Subject: {email.subject}")
        print(f"      Date: {email.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n6. Viewing Alice's inbox...")
    alice_inbox = service.get_inbox("alice@example.com")
    print(f"   Alice has {len(alice_inbox)} email(s) in her inbox:")
    for i, email in enumerate(alice_inbox, 1):
        status = "[Read]" if email.read else "[Unread]"
        print(f"   {i}. {status} From: {email.sender}")
        print(f"      Subject: {email.subject}")
    
    print("\n7. Listing all registered users...")
    all_users = service.list_users()
    print(f"   Total users: {len(all_users)}")
    for i, user in enumerate(all_users, 1):
        print(f"   {i}. {user}")
    
    print("\n" + "=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)
    print("\nTo try the interactive CLI, run: python main.py")


if __name__ == "__main__":
    main()
