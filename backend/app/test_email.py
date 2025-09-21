#!/usr/bin/env python3
"""
Email Configuration Test Script
"""

import smtplib
import ssl
import socket
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_configuration():
    # Load environment variables
    load_dotenv()
    
    print('=== EMAIL CONFIGURATION TEST ===')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    email_from = os.getenv('EMAIL_FROM', 'Smart Rental Tracker')
    
    print(f'SMTP Server: {smtp_server}')
    print(f'SMTP Port: {smtp_port}')
    print(f'Username: {smtp_username}')
    print(f'Password: {"***" if smtp_password else "None"}')
    print(f'From: {email_from}')
    
    if not smtp_username or not smtp_password:
        print('ERROR: Missing username or password in .env file')
        return False
    
    print('\n=== Testing Network Connectivity ===')
    try:
        # Test if we can reach the SMTP server
        sock = socket.create_connection((smtp_server, smtp_port), timeout=10)
        sock.close()
        print('✓ Network connectivity to SMTP server is working')
    except Exception as e:
        print(f'✗ Network connectivity failed: {e}')
        return False
    
    print('\n=== Testing SMTP Connection (Method 1: Standard) ===')
    try:
        print('Step 1: Connecting to SMTP server...')
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        print('✓ Connected to SMTP server')
        
        print('Step 2: Starting TLS...')
        server.starttls()
        print('✓ TLS connection established')
        
        print('Step 3: Attempting login...')
        server.login(smtp_username, smtp_password)
        print('✓ Login successful')
        
        print('Step 4: Closing connection...')
        server.quit()
        print('✓ Connection closed properly')
        print('SUCCESS: Email configuration is working!')
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f'✗ Authentication failed: {e}')
        print('Solutions:')
        print('1. Check if 2-factor authentication is enabled on Gmail')
        print('2. Generate a new App Password: https://myaccount.google.com/apppasswords')
        print('3. Use the App Password instead of your regular Gmail password')
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f'✗ Connection failed: {e}')
        print('Solutions:')
        print('1. Check internet connection')
        print('2. Try using port 465 with SSL instead of 587 with TLS')
        return False
        
    except Exception as e:
        print(f'✗ Unexpected error: {type(e).__name__}: {e}')
        
        # Try alternative method with SSL
        print('\n=== Testing SMTP Connection (Method 2: SSL) ===')
        try:
            print('Trying with SSL on port 465...')
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context, timeout=30)
            server.login(smtp_username, smtp_password)
            print('✓ SSL connection successful!')
            server.quit()
            
            # Update recommendation
            print('\nRECOMMENDATION: Update your .env file to use:')
            print('SMTP_SERVER=smtp.gmail.com')
            print('SMTP_PORT=465')
            print('And modify the notification service to use SMTP_SSL instead of SMTP with starttls()')
            return True
            
        except Exception as e2:
            print(f'✗ SSL method also failed: {type(e2).__name__}: {e2}')
            return False

def test_send_email():
    """Test sending an actual email"""
    load_dotenv()
    
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    email_from = os.getenv('EMAIL_FROM', 'Smart Rental Tracker')
    
    print('\n=== TESTING ACTUAL EMAIL SEND ===')
    
    # Create test email
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = smtp_username  # Send to self for testing
    msg['Subject'] = 'Smart Rental Tracker - Email Configuration Test'
    
    body = """
    This is a test email from the Smart Rental Tracker notification system.
    
    If you receive this email, your email configuration is working correctly!
    
    Test Details:
    - Sent from: Smart Rental Tracker Notification System
    - Date: """ + str(datetime.now()) + """
    - Purpose: Email configuration verification
    
    Best regards,
    Smart Rental Tracker System
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        text = msg.as_string()
        server.sendmail(email_from, smtp_username, text)
        server.quit()
        
        print(f'✓ Test email sent successfully to {smtp_username}')
        print('Check your inbox for the test email!')
        return True
        
    except Exception as e:
        print(f'✗ Failed to send test email: {e}')
        return False

if __name__ == "__main__":
    print("Smart Rental Tracker - Email Configuration Test")
    print("=" * 50)
    
    # Test connection
    connection_ok = test_email_configuration()
    
    if connection_ok:
        # Ask if user wants to send test email
        print("\n" + "=" * 50)
        response = input("Send a test email? (y/n): ").lower().strip()
        if response == 'y':
            from datetime import datetime
            test_send_email()
    
    print("\n" + "=" * 50)
    print("Email configuration test complete!")
