"""
Notification Service for Smart Rental Tracker
Handles automated email notifications for equipment return reminders
"""

import smtplib
import schedule
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
from app.database import SessionLocal
from app.models import Equipment
from typing import List, Dict, Any
import logging

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notifications.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.email_from = os.getenv('EMAIL_FROM', 'Smart Rental Tracker')
        self.notification_days_ahead = int(os.getenv('NOTIFICATION_DAYS_AHEAD', '7'))
        
        # Debug logging
        logger.info(f"Email config - Server: {self.smtp_server}, Port: {self.smtp_port}")
        logger.info(f"Email config - Username: {'***' if self.smtp_username else 'None'}")
        logger.info(f"Email config - Password: {'***' if self.smtp_password else 'None'}")
        
    def get_upcoming_returns(self) -> List[Dict[str, Any]]:
        """Get equipment with upcoming return dates within notification window"""
        db = SessionLocal()
        try:
            from datetime import datetime
            from sqlalchemy import and_
            
            # Get equipment that is currently rented (has site_id and check_in_date)
            equipment_list = db.query(Equipment).filter(
                and_(
                    Equipment.site_id.isnot(None),  # Currently rented
                    Equipment.check_in_date.isnot(None)  # Has expected return date
                )
            ).all()
            
            rental_data = []
            for equipment in equipment_list:
                # Parse check_in_date as expected return date
                try:
                    if equipment.check_in_date:
                        # Assuming check_in_date is stored as string in "YYYY-MM-DD" format
                        from datetime import datetime
                        if isinstance(equipment.check_in_date, str):
                            expected_return = datetime.strptime(equipment.check_in_date, '%Y-%m-%d')
                        else:
                            expected_return = equipment.check_in_date
                        
                        # Check if return is within notification window
                        days_until_return = (expected_return.date() - datetime.now().date()).days
                        
                        if 0 <= days_until_return <= self.notification_days_ahead:
                            # Parse check_out_date if it's a string
                            check_out_parsed = None
                            if equipment.check_out_date:
                                if isinstance(equipment.check_out_date, str):
                                    try:
                                        check_out_parsed = datetime.strptime(equipment.check_out_date, '%Y-%m-%d')
                                    except ValueError:
                                        # Try alternative format
                                        try:
                                            check_out_parsed = datetime.strptime(equipment.check_out_date, '%m/%d/%Y')
                                        except ValueError:
                                            check_out_parsed = datetime.now()  # Fallback
                                else:
                                    check_out_parsed = equipment.check_out_date
                            else:
                                check_out_parsed = datetime.now()  # Fallback if no date
                            
                            rental_data.append({
                                'equipment_id': equipment.equipment_id,
                                'equipment_name': f"{equipment.type} {equipment.model}" if equipment.model else equipment.type,
                                'equipment_type': equipment.type,
                                'equipment_serial': equipment.serial_number or equipment.equipment_id,
                                'operator_name': equipment.last_operator_id or "Unknown Operator",
                                'operator_email': f"{equipment.last_operator_id}@company.com" if equipment.last_operator_id else "operator@company.com",
                                'operator_phone': "N/A",
                                'site_name': f"Site {equipment.site_id}" if equipment.site_id else "Unknown Site",
                                'site_contact_email': f"{equipment.site_id}@company.com" if equipment.site_id else "site@company.com",
                                'site_contact_phone': "N/A",
                                'check_out_date': check_out_parsed,
                                'expected_return_date': expected_return,
                                'rental_rate': 500.0  # Default daily rate
                            })
                except Exception as e:
                    logger.warning(f"Error processing equipment {equipment.equipment_id}: {e}")
                    continue
            
            return rental_data
            
        except Exception as e:
            logger.error(f"Error fetching upcoming returns: {e}")
            return []
        finally:
            db.close()
    
    def get_overdue_rentals(self) -> List[Dict[str, Any]]:
        """Get equipment with overdue returns"""
        db = SessionLocal()
        try:
            from datetime import datetime
            from sqlalchemy import and_
            
            # Get equipment that is currently rented and overdue
            equipment_list = db.query(Equipment).filter(
                and_(
                    Equipment.site_id.isnot(None),  # Currently rented
                    Equipment.check_in_date.isnot(None)  # Has expected return date
                )
            ).all()
            
            rental_data = []
            today = datetime.now().date()
            
            for equipment in equipment_list:
                try:
                    if equipment.check_in_date:
                        # Parse expected return date
                        if isinstance(equipment.check_in_date, str):
                            expected_return = datetime.strptime(equipment.check_in_date, '%Y-%m-%d')
                        else:
                            expected_return = equipment.check_in_date
                        
                        # Check if overdue
                        if expected_return.date() < today:
                            days_overdue = (today - expected_return.date()).days
                            
                            # Parse check_out_date if it's a string
                            check_out_parsed = None
                            if equipment.check_out_date:
                                if isinstance(equipment.check_out_date, str):
                                    try:
                                        check_out_parsed = datetime.strptime(equipment.check_out_date, '%Y-%m-%d')
                                    except ValueError:
                                        # Try alternative format
                                        try:
                                            check_out_parsed = datetime.strptime(equipment.check_out_date, '%m/%d/%Y')
                                        except ValueError:
                                            check_out_parsed = datetime.now()  # Fallback
                                else:
                                    check_out_parsed = equipment.check_out_date
                            else:
                                check_out_parsed = datetime.now()  # Fallback if no date
                            
                            rental_data.append({
                                'equipment_id': equipment.equipment_id,
                                'equipment_name': f"{equipment.type} {equipment.model}" if equipment.model else equipment.type,
                                'equipment_type': equipment.type,
                                'equipment_serial': equipment.serial_number or equipment.equipment_id,
                                'operator_name': equipment.last_operator_id or "Unknown Operator",
                                'operator_email': f"{equipment.last_operator_id}@company.com" if equipment.last_operator_id else "operator@company.com",
                                'operator_phone': "N/A",
                                'site_name': f"Site {equipment.site_id}" if equipment.site_id else "Unknown Site",
                                'site_contact_email': f"{equipment.site_id}@company.com" if equipment.site_id else "site@company.com",
                                'site_contact_phone': "N/A",
                                'check_out_date': check_out_parsed,
                                'expected_return_date': expected_return,
                                'days_overdue': days_overdue,
                                'rental_rate': 500.0  # Default daily rate
                            })
                except Exception as e:
                    logger.warning(f"Error processing equipment {equipment.equipment_id}: {e}")
                    continue
            
            return rental_data
            
        except Exception as e:
            logger.error(f"Error fetching overdue rentals: {e}")
            return []
        finally:
            db.close()
    
    def create_return_reminder_email(self, rental_data: Dict[str, Any]) -> MIMEMultipart:
        """Create return reminder email"""
        msg = MIMEMultipart()
        msg['From'] = self.email_from
        msg['To'] = rental_data['operator_email']
        msg['Subject'] = f"Equipment Return Reminder - {rental_data['equipment_name']}"
        
        # Format dates safely
        checkout_date_str = "N/A"
        expected_return_str = "N/A"
        
        try:
            if rental_data['check_out_date'] and hasattr(rental_data['check_out_date'], 'strftime'):
                checkout_date_str = rental_data['check_out_date'].strftime('%B %d, %Y')
        except (AttributeError, ValueError, TypeError):
            checkout_date_str = str(rental_data['check_out_date']) if rental_data['check_out_date'] else "N/A"
        
        try:
            if rental_data['expected_return_date'] and hasattr(rental_data['expected_return_date'], 'strftime'):
                expected_return_str = rental_data['expected_return_date'].strftime('%B %d, %Y')
        except (AttributeError, ValueError, TypeError):
            expected_return_str = str(rental_data['expected_return_date']) if rental_data['expected_return_date'] else "N/A"
        
        # Email body
        body = f"""
Dear {rental_data['operator_name']},

This is a friendly reminder that your rental equipment is due for return in {self.notification_days_ahead} days.

Equipment Details:
• Equipment: {rental_data['equipment_name']} ({rental_data['equipment_type']})
• Serial Number: {rental_data['equipment_serial']}
• Site: {rental_data['site_name']}
• Checkout Date: {checkout_date_str}
• Expected Return Date: {expected_return_str}
• Daily Rate: ${rental_data['rental_rate']:,.2f}

Please ensure the equipment is returned on time to avoid late fees. If you need to extend the rental period, please contact us immediately.

Site Contact Information:
• Email: {rental_data['site_contact_email']}
• Phone: {rental_data['site_contact_phone']}

Thank you for your business!

Best regards,
Smart Rental Tracker System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        return msg
    
    def create_overdue_email(self, rental_data: Dict[str, Any]) -> MIMEMultipart:
        """Create overdue rental email"""
        msg = MIMEMultipart()
        msg['From'] = self.email_from
        msg['To'] = rental_data['operator_email']
        msg['Subject'] = f"OVERDUE: Equipment Return Required - {rental_data['equipment_name']}"
        
        # Calculate late fees (assuming 10% daily penalty)
        late_fee = rental_data['rental_rate'] * 0.1 * rental_data['days_overdue']
        
        # Format dates safely
        checkout_date_str = "N/A"
        expected_return_str = "N/A"
        
        try:
            if rental_data['check_out_date'] and hasattr(rental_data['check_out_date'], 'strftime'):
                checkout_date_str = rental_data['check_out_date'].strftime('%B %d, %Y')
        except (AttributeError, ValueError, TypeError):
            checkout_date_str = str(rental_data['check_out_date']) if rental_data['check_out_date'] else "N/A"
        
        try:
            if rental_data['expected_return_date'] and hasattr(rental_data['expected_return_date'], 'strftime'):
                expected_return_str = rental_data['expected_return_date'].strftime('%B %d, %Y')
        except (AttributeError, ValueError, TypeError):
            expected_return_str = str(rental_data['expected_return_date']) if rental_data['expected_return_date'] else "N/A"
        
        body = f"""
Dear {rental_data['operator_name']},

URGENT: Your rental equipment is now {rental_data['days_overdue']} days overdue for return.

Equipment Details:
• Equipment: {rental_data['equipment_name']} ({rental_data['equipment_type']})
• Serial Number: {rental_data['equipment_serial']}
• Site: {rental_data['site_name']}
• Checkout Date: {checkout_date_str}
• Expected Return Date: {expected_return_str}
• Days Overdue: {rental_data['days_overdue']}
• Daily Rate: ${rental_data['rental_rate']:,.2f}
• Estimated Late Fees: ${late_fee:,.2f}

IMMEDIATE ACTION REQUIRED:
Please return the equipment as soon as possible to minimize additional charges.

Site Contact Information:
• Email: {rental_data['site_contact_email']}
• Phone: {rental_data['site_contact_phone']}

If you have already returned the equipment, please disregard this message and contact us to update our records.

Best regards,
Smart Rental Tracker System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        return msg
    
    def send_email(self, msg: MIMEMultipart) -> bool:
        """Send email via SMTP"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.email_from, msg['To'], text)
            server.quit()
            
            logger.info(f"Email sent successfully to {msg['To']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {msg['To']}: {e}")
            return False
    
    def send_return_reminders(self):
        """Send return reminder emails for upcoming due dates"""
        logger.info("Starting return reminder notifications...")
        
        upcoming_rentals = self.get_upcoming_returns()
        
        if not upcoming_rentals:
            logger.info("No upcoming returns found")
            return
        
        logger.info(f"Found {len(upcoming_rentals)} upcoming returns")
        
        sent_count = 0
        for rental in upcoming_rentals:
            if rental['operator_email']:
                email = self.create_return_reminder_email(rental)
                if self.send_email(email):
                    sent_count += 1
            else:
                logger.warning(f"No email address for operator: {rental['operator_name']}")
        
        logger.info(f"Sent {sent_count} return reminder emails")
    
    def send_overdue_notifications(self):
        """Send overdue rental notifications"""
        logger.info("Starting overdue rental notifications...")
        
        overdue_rentals = self.get_overdue_rentals()
        
        if not overdue_rentals:
            logger.info("No overdue rentals found")
            return
        
        logger.info(f"Found {len(overdue_rentals)} overdue rentals")
        
        sent_count = 0
        for rental in overdue_rentals:
            if rental['operator_email']:
                email = self.create_overdue_email(rental)
                if self.send_email(email):
                    sent_count += 1
            else:
                logger.warning(f"No email address for operator: {rental['operator_name']}")
        
        logger.info(f"Sent {sent_count} overdue rental emails")
    
    def test_email_configuration(self) -> bool:
        """Test email configuration"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.quit()
            logger.info("Email configuration test successful")
            return True
        except Exception as e:
            logger.error(f"Email configuration test failed: {e}")
            return False

def run_scheduled_notifications():
    """Main function to run scheduled notifications"""
    notification_service = NotificationService()
    
    # Test email configuration first
    if not notification_service.test_email_configuration():
        logger.error("Email configuration invalid. Please check your .env file settings.")
        return
    
    # Send return reminders
    notification_service.send_return_reminders()
    
    # Send overdue notifications
    notification_service.send_overdue_notifications()

def start_notification_scheduler():
    """Start the notification scheduler"""
    logger.info("Starting notification scheduler...")
    
    # Schedule return reminders to run daily at 9 AM
    schedule.every().day.at("09:00").do(run_scheduled_notifications)
    
    # Also run overdue notifications daily at 2 PM
    schedule.every().day.at("14:00").do(lambda: NotificationService().send_overdue_notifications())
    
    logger.info("Notification scheduler started. Notifications will run daily at 9 AM and 2 PM")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # For testing purposes
    notification_service = NotificationService()
    
    print("Testing notification service...")
    print("1. Testing email configuration...")
    if notification_service.test_email_configuration():
        print("✓ Email configuration successful")
    else:
        print("✗ Email configuration failed")
    
    print("\n2. Checking upcoming returns...")
    upcoming = notification_service.get_upcoming_returns()
    print(f"Found {len(upcoming)} upcoming returns")
    
    print("\n3. Checking overdue rentals...")
    overdue = notification_service.get_overdue_rentals()
    print(f"Found {len(overdue)} overdue rentals")
    
    # Uncomment to test actual email sending (make sure .env is configured)
    # print("\n4. Sending test notifications...")
    # notification_service.send_return_reminders()
    # notification_service.send_overdue_notifications()
