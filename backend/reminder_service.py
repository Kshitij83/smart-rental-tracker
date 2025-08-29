"""
Email notification service for Smart Rental Tracking System
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, date
from typing import List
import sys
from sqlalchemy import Date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the correct working directory for database access
backend_dir = os.path.dirname(__file__)
os.chdir(backend_dir)

# Add the app directory to the path
sys.path.append(os.path.join(backend_dir, 'app'))

from app.database import SessionLocal
from app.models import Rental, Equipment, Operator, Site
from app import schemas
from app import crud

class EmailService:
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("EMAIL_PORT", "587"))
        self.email_address = os.getenv("EMAIL_ADDRESS", "your-email@company.com")
        self.email_password = os.getenv("EMAIL_PASSWORD", "your-app-password")
        self.company_name = os.getenv("COMPANY_NAME", "Smart Rental Equipment Co.")
        
        # Check if email is configured
        if self.email_address == "your-email@company.com" or self.email_password == "your-app-password":
            print("⚠️ WARNING: Email not configured! Please update .env file with your email credentials.")
            print("📋 Copy .env.example to .env and update with your settings.")
        
    def send_email(self, to_email: str, subject: str, body: str, to_name: str = ""):
        """Send an email notification"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.company_name} <{self.email_address}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach body
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            print(f"✅ Email sent to {to_name} ({to_email})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def create_reminder_email_body(self, rental_info: dict) -> str:
        """Create HTML email body for rental reminder"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5aa0;">Equipment Return Reminder</h2>
                
                <p>Dear {rental_info['operator_name']},</p>
                
                <p>This is a friendly reminder that your rented equipment is due for return in <strong>7 days</strong>.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #495057;">Rental Details:</h3>
                    <p><strong>Equipment:</strong> {rental_info['equipment_type']} - {rental_info['equipment_id']}</p>
                    <p><strong>Model:</strong> {rental_info['equipment_model']}</p>
                    <p><strong>Check-out Date:</strong> {rental_info['check_out_date']}</p>
                    <p><strong>Due Date:</strong> <span style="color: #dc3545; font-weight: bold;">{rental_info['due_date']}</span></p>
                    <p><strong>Site:</strong> {rental_info['site_name']}</p>
                    <p><strong>Days Remaining:</strong> <span style="color: #28a745; font-weight: bold;">7 days</span></p>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                    <h4 style="margin-top: 0; color: #856404;">Important Reminders:</h4>
                    <ul>
                        <li>Please ensure the equipment is cleaned and in good condition</li>
                        <li>Complete any pending maintenance checks</li>
                        <li>Return all accessories and documentation</li>
                        <li>Contact us if you need to extend the rental period</li>
                    </ul>
                </div>
                
                <div style="margin: 30px 0;">
                    <h4>Need to extend your rental?</h4>
                    <p>Contact us immediately to avoid late fees:</p>
                    <p>📞 Phone: +1-555-RENTAL (735-8255)</p>
                    <p>📧 Email: rentals@smartequipment.com</p>
                </div>
                
                <div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Return Location:</strong><br>
                    Smart Rental Equipment Co.<br>
                    123 Industrial Park Drive<br>
                    Equipment City, EC 12345</p>
                </div>
                
                <p>Thank you for choosing {self.company_name}!</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                <p style="font-size: 12px; color: #6c757d;">
                    This is an automated reminder from our rental management system. 
                    Please do not reply to this email. For assistance, contact our customer service team.
                </p>
            </div>
        </body>
        </html>
        """

class RentalReminderService:
    def __init__(self):
        self.email_service = EmailService()
        self.db = SessionLocal()
    
    def get_rentals_due_in_days(self, days: int = 7) -> List[dict]:
        """Get rentals that are due in specified number of days"""
        target_date = datetime.now().date() + timedelta(days=days)
        
        # Query active rentals due on the target date
        rentals = self.db.query(Rental).filter(
            Rental.status == "active",
            Rental.expected_return_date.cast(Date) == target_date
        ).all()
        
        rental_info = []
        for rental in rentals:
            # Get related information
            equipment = self.db.query(Equipment).filter(Equipment.id == rental.equipment_id).first()
            operator = self.db.query(Operator).filter(Operator.id == rental.operator_id).first()
            site = self.db.query(Site).filter(Site.id == rental.site_id).first()
            
            if equipment and operator and operator.email:
                rental_info.append({
                    'rental_id': rental.id,
                    'operator_name': operator.name,
                    'operator_email': operator.email,
                    'operator_phone': operator.phone,
                    'equipment_id': equipment.equipment_id,
                    'equipment_type': equipment.type,
                    'equipment_model': equipment.model or 'N/A',
                    'check_out_date': rental.check_out_date.strftime('%Y-%m-%d'),
                    'due_date': rental.expected_return_date.strftime('%Y-%m-%d'),
                    'site_name': site.name if site else 'N/A',
                    'days_remaining': days
                })
        
        return rental_info
    
    def send_reminder_notifications(self, days_ahead: int = 7):
        """Send reminder emails to operators for rentals due in specified days"""
        print(f"🔍 Checking for rentals due in {days_ahead} days...")
        
        rentals_due = self.get_rentals_due_in_days(days_ahead)
        
        if not rentals_due:
            print(f"✅ No rentals due in {days_ahead} days.")
            return
        
        print(f"📧 Found {len(rentals_due)} rental(s) due for reminder notifications:")
        
        sent_count = 0
        failed_count = 0
        
        for rental in rentals_due:
            print(f"\n📋 Processing: {rental['equipment_id']} - {rental['operator_name']}")
            
            # Create email subject and body
            subject = f"⏰ Equipment Return Reminder - {rental['equipment_id']} Due in {days_ahead} Days"
            body = self.email_service.create_reminder_email_body(rental)
            
            # Send email
            success = self.email_service.send_email(
                to_email=rental['operator_email'],
                subject=subject,
                body=body,
                to_name=rental['operator_name']
            )
            
            if success:
                sent_count += 1
                # Log the notification in the database
                self.log_notification(rental)
            else:
                failed_count += 1
        
        print(f"\n📊 Notification Summary:")
        print(f"   ✅ Sent: {sent_count}")
        print(f"   ❌ Failed: {failed_count}")
        
        # Create alerts for failed notifications
        if failed_count > 0:
            self.create_failed_notification_alert(failed_count)
    
    def log_notification(self, rental_info: dict):
        """Log the sent notification as an alert in the database"""
        try:
            alert_data = schemas.AlertCreate(
                rental_id=rental_info['rental_id'],
                alert_type="reminder_sent",
                severity="low",
                title=f"Return Reminder Sent - {rental_info['equipment_id']}",
                description=f"7-day return reminder email sent to {rental_info['operator_name']} ({rental_info['operator_email']})"
            )
            crud.create_alert(self.db, alert_data)
            self.db.commit()
        except Exception as e:
            print(f"⚠️ Failed to log notification: {e}")
    
    def create_failed_notification_alert(self, failed_count: int):
        """Create an alert for failed notifications"""
        try:
            alert_data = schemas.AlertCreate(
                alert_type="system_error",
                severity="medium",
                title=f"Failed to Send {failed_count} Reminder Notifications",
                description=f"System failed to send {failed_count} rental reminder email(s). Check email configuration and operator contact information."
            )
            crud.create_alert(self.db, alert_data)
            self.db.commit()
        except Exception as e:
            print(f"⚠️ Failed to create failed notification alert: {e}")
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

def run_daily_reminders():
    """Main function to run daily reminder checks"""
    print("🚀 Starting Daily Rental Reminder Service...")
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    reminder_service = RentalReminderService()
    
    try:
        # Send 7-day reminders
        reminder_service.send_reminder_notifications(days_ahead=7)
        
        # You can also add 3-day and 1-day reminders
        # reminder_service.send_reminder_notifications(days_ahead=3)
        # reminder_service.send_reminder_notifications(days_ahead=1)
        
    except Exception as e:
        print(f"❌ Error in reminder service: {e}")
    
    print("✅ Daily reminder service completed!")

if __name__ == "__main__":
    run_daily_reminders()
