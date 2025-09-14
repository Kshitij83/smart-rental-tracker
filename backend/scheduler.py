"""
Automated scheduler for rental reminder notifications
Runs daily at 9:00 AM to check for rentals due in 7 days
"""
import schedule
import time
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from reminder_service import run_daily_reminders

def job():
    """Job function to be scheduled"""
    print("\n" + "="*50)
    print(f"📅 Scheduled Reminder Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    try:
        run_daily_reminders()
    except Exception as e:
        print(f"❌ Scheduler error: {e}")
    
    print("="*50)
    print("⏰ Next check scheduled for tomorrow at 9:00 AM")
    print("="*50 + "\n")

def start_scheduler():
    """Start the automated scheduler"""
    print("🤖 Smart Rental Tracking - Automated Reminder Service")
    print("⏰ Scheduling daily reminders at 9:00 AM...")
    
    # Schedule the job to run daily at 9:00 AM
    schedule.every().day.at("09:00").do(job)
    
    # Also allow manual testing
    print("💡 For testing purposes, you can run reminders every minute by uncommenting the line below")
    # schedule.every(1).minutes.do(job)  # Uncomment for testing
    
    print("✅ Scheduler started successfully!")
    print("🔄 Service is running... Press Ctrl+C to stop")
    
    # Run the job once immediately for testing
    print("\n🧪 Running initial check...")
    job()
    
    try:
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        print("\n\n⏹️ Scheduler stopped by user")
        print("👋 Goodbye!")

if __name__ == "__main__":
    start_scheduler()
