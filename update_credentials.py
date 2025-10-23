#!/usr/bin/env python3
"""
Quick script to update .env file with credentials
"""
import os
import sys

def update_env(email, password):
    """Update .env file with credentials"""

    # Read current .env
    with open('.env', 'r') as f:
        content = f.read()

    # Replace placeholder credentials
    content = content.replace('IQOPTION_EMAIL=your_email@example.com', f'IQOPTION_EMAIL={email}')
    content = content.replace('IQOPTION_PASSWORD=your_password_here', f'IQOPTION_PASSWORD={password}')

    # Write back
    with open('.env', 'w') as f:
        f.write(content)

    # Set permissions
    os.chmod('.env', 0o600)

    print("✅ Credentials updated in .env file")
    print(f"   Email: {email}")
    print(f"   Mode: demo")
    print()
    print("Ready to run tests!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 update_credentials.py <email> <password>")
        print("Example: python3 update_credentials.py myemail@example.com mypassword")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    update_env(email, password)
