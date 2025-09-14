"""
Notification Scheduler
Runs the notification service on a schedule to automatically send emails
"""

import os
import sys
import time
import schedule
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from notification_service import NotificationService
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_notifications():
    """Run the notification service"""
    logger.info("=" * 50)
    logger.info(f"Starting scheduled notification run at {datetime.now()}")
    
    try:
        notification_service = NotificationService()
        
        # Test email configuration
        if not notification_service.test_email_configuration():
            logger.error("Email configuration test failed. Skipping notification run.")
            return
        
        # Send return reminders
        logger.info("Sending return reminders...")
        notification_service.send_return_reminders()
        
        # Send overdue notifications
        logger.info("Sending overdue notifications...")
        notification_service.send_overdue_notifications()
        
        logger.info("Scheduled notification run completed successfully")
        
    except Exception as e:
        logger.error(f"Error in scheduled notification run: {e}")
    
    logger.info("=" * 50)

def start_scheduler():
    """Start the notification scheduler"""
    logger.info("Starting Smart Rental Tracker Notification Scheduler")
    logger.info("Schedule:")
    logger.info("  - Return reminders: Daily at 9:00 AM")
    logger.info("  - Overdue notifications: Daily at 2:00 PM")
    logger.info("  - Full notification check: Daily at 6:00 PM")
    
    # Schedule return reminders to run daily at 9 AM
    schedule.every().day.at("09:00").do(
        lambda: NotificationService().send_return_reminders()
    ).tag('return_reminders')
    
    # Schedule overdue notifications to run daily at 2 PM
    schedule.every().day.at("14:00").do(
        lambda: NotificationService().send_overdue_notifications()
    ).tag('overdue_notifications')
    
    # Schedule a full notification check daily at 6 PM
    schedule.every().day.at("18:00").do(run_notifications).tag('full_check')
    
    logger.info("Scheduler started. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Rental Tracker Notification Scheduler')
    parser.add_argument('--test', action='store_true', help='Run a test notification immediately')
    parser.add_argument('--config-test', action='store_true', help='Test email configuration only')
    args = parser.parse_args()
    
    if args.config_test:
        # Test email configuration
        notification_service = NotificationService()
        if notification_service.test_email_configuration():
            print("✓ Email configuration is valid")
        else:
            print("✗ Email configuration test failed")
            sys.exit(1)
    
    elif args.test:
        # Run a test notification immediately
        print("Running test notification...")
        run_notifications()
    
    else:
        # Start the scheduler
        start_scheduler()
