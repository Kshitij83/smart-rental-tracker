"""
Smart Rental Tracker Notification Service
Handles automated email notifications for rental reminders and overdue alerts
"""

import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from . import models, crud
from .database import get_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        """Initialize the notification service with email configuration"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_name = os.getenv('SENDER_NAME', 'Smart Rental Tracker')
        
        # EmailJS configuration (alternative to SMTP)
        self.emailjs_service_id = os.getenv('EMAILJS_SERVICE_ID', '')
        self.emailjs_template_id = os.getenv('EMAILJS_TEMPLATE_ID', '')
        self.emailjs_user_id = os.getenv('EMAILJS_USER_ID', '')
        self.emailjs_url = "https://api.emailjs.com/api/v1.0/email/send"
        
        # Notification settings
        self.reminder_days_before = 7  # Send reminder 7 days before return
        self.overdue_alert_hours = 24  # Send overdue alert after 24 hours
        
    def test_email_configuration(self) -> bool:
        """Test if email configuration is valid"""
        try:
            if self.smtp_username and self.smtp_password:
                # Test SMTP connection
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                logger.info("SMTP configuration test successful")
                return True
            elif self.emailjs_service_id and self.emailjs_template_id and self.emailjs_user_id:
                # Test EmailJS configuration
                logger.info("EmailJS configuration detected")
                return True
            else:
                logger.error("No valid email configuration found")
                return False
        except Exception as e:
            logger.error(f"Email configuration test failed: {e}")
            return False
    
    def send_email_smtp(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text and HTML parts
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_email_emailjs(self, to_email: str, subject: str, body: str, template_params: Dict = None) -> bool:
        """Send email using EmailJS"""
        try:
            if not all([self.emailjs_service_id, self.emailjs_template_id, self.emailjs_user_id]):
                logger.error("EmailJS configuration incomplete")
                return False
            
            # Prepare template parameters
            if template_params is None:
                template_params = {}
            
            template_params.update({
                'to_email': to_email,
                'subject': subject,
                'message': body
            })
            
            # Send request to EmailJS
            response = requests.post(
                self.emailjs_url,
                json={
                    'service_id': self.emailjs_service_id,
                    'template_id': self.emailjs_template_id,
                    'user_id': self.emailjs_user_id,
                    'template_params': template_params
                }
            )
            
            if response.status_code == 200:
                logger.info(f"EmailJS email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"EmailJS request failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send EmailJS email to {to_email}: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None, 
                   template_params: Dict = None) -> bool:
        """Send email using available method (SMTP or EmailJS)"""
        # Try SMTP first, then EmailJS
        if self.smtp_username and self.smtp_password:
            return self.send_email_smtp(to_email, subject, body, html_body)
        elif self.emailjs_service_id and self.emailjs_template_id and self.emailjs_user_id:
            return self.send_email_emailjs(to_email, subject, body, template_params)
        else:
            logger.error("No email method configured")
            return False
    
    def get_rentals_due_soon(self, db: Session, days_ahead: int = 7) -> List[models.Rental]:
        """Get rentals that are due within the specified number of days"""
        current_time = datetime.utcnow()
        target_date = current_time + timedelta(days=days_ahead)
        
        return db.query(models.Rental).filter(
            models.Rental.status == "active",
            models.Rental.expected_return_date <= target_date,
            models.Rental.expected_return_date > current_time
        ).all()
    
    def get_overdue_rentals(self, db: Session) -> List[models.Rental]:
        """Get rentals that are overdue"""
        current_time = datetime.utcnow()
        
        return db.query(models.Rental).filter(
            models.Rental.status == "active",
            models.Rental.expected_return_date < current_time
        ).all()
    
    def send_return_reminders(self) -> Dict:
        """Send reminders for equipment due to be returned soon"""
        logger.info("Sending return reminders...")
        
        try:
            db = next(get_db())
            rentals_due_soon = self.get_rentals_due_soon(db, self.reminder_days_before)
            
            reminders_sent = 0
            failed_reminders = 0
            
            for rental in rentals_due_soon:
                try:
                    # Get contact information
                    site = rental.site
                    operator = rental.operator
                    
                    if not site or not site.contact_person:
                        logger.warning(f"No contact person for site {rental.site_id}")
                        continue
                    
                    # Calculate days until return
                    days_until_return = (rental.expected_return_date - datetime.utcnow()).days
                    
                    # Prepare email content
                    subject = f"Equipment Return Reminder - {rental.equipment.equipment_id}"
                    
                    body = f"""
Dear {site.contact_person},

This is a friendly reminder that the following equipment is due to be returned:

Equipment ID: {rental.equipment.equipment_id}
Equipment Type: {rental.equipment.type}
Rental Start Date: {rental.check_out_date.strftime('%Y-%m-%d')}
Expected Return Date: {rental.expected_return_date.strftime('%Y-%m-%d')}
Days Until Return: {days_until_return}

Please ensure the equipment is returned on time to avoid any additional charges.

If you need to extend the rental period, please contact us immediately.

Best regards,
{self.sender_name}
                    """.strip()
                    
                    html_body = f"""
<html>
<body>
<h2>Equipment Return Reminder</h2>
<p>Dear {site.contact_person},</p>
<p>This is a friendly reminder that the following equipment is due to be returned:</p>
<ul>
<li><strong>Equipment ID:</strong> {rental.equipment.equipment_id}</li>
<li><strong>Equipment Type:</strong> {rental.equipment.type}</li>
<li><strong>Rental Start Date:</strong> {rental.check_out_date.strftime('%Y-%m-%d')}</li>
<li><strong>Expected Return Date:</strong> {rental.expected_return_date.strftime('%Y-%m-%d')}</li>
<li><strong>Days Until Return:</strong> {days_until_return}</li>
</ul>
<p>Please ensure the equipment is returned on time to avoid any additional charges.</p>
<p>If you need to extend the rental period, please contact us immediately.</p>
<p>Best regards,<br>{self.sender_name}</p>
</body>
</html>
                    """.strip()
                    
                    # Send reminder email
                    if self.send_email(site.contact_person, subject, body, html_body):
                        reminders_sent += 1
                        
                        # Create alert record
                        alert = models.Alert(
                            rental_id=rental.id,
                            equipment_id=rental.equipment_id,
                            alert_type="return_reminder",
                            severity="medium",
                            title=f"Return reminder sent for {rental.equipment.equipment_id}",
                            description=f"Reminder sent to {site.contact_person} about equipment due in {days_until_return} days"
                        )
                        db.add(alert)
                        
                    else:
                        failed_reminders += 1
                        
                except Exception as e:
                    logger.error(f"Error sending reminder for rental {rental.id}: {e}")
                    failed_reminders += 1
            
            # Commit all alerts
            db.commit()
            
            logger.info(f"Return reminders completed: {reminders_sent} sent, {failed_reminders} failed")
            
            return {
                "reminders_sent": reminders_sent,
                "failed_reminders": failed_reminders,
                "total_rentals_checked": len(rentals_due_soon)
            }
            
        except Exception as e:
            logger.error(f"Error in send_return_reminders: {e}")
            return {"error": str(e)}
    
    def send_overdue_notifications(self) -> Dict:
        """Send notifications for overdue equipment"""
        logger.info("Sending overdue notifications...")
        
        try:
            db = next(get_db())
            overdue_rentals = self.get_overdue_rentals(db)
            
            overdue_notifications_sent = 0
            failed_notifications = 0
            
            for rental in overdue_rentals:
                try:
                    # Get contact information
                    site = rental.site
                    operator = rental.operator
                    
                    if not site or not site.contact_person:
                        logger.warning(f"No contact person for site {rental.site_id}")
                        continue
                    
                    # Calculate overdue days
                    overdue_days = (datetime.utcnow() - rental.expected_return_date).days
                    
                    # Prepare email content
                    subject = f"URGENT: Equipment Overdue - {rental.equipment.equipment_id}"
                    
                    body = f"""
URGENT NOTICE

Dear {site.contact_person},

The following equipment is OVERDUE and must be returned immediately:

Equipment ID: {rental.equipment.equipment_id}
Equipment Type: {rental.equipment.type}
Rental Start Date: {rental.check_out_date.strftime('%Y-%m-%d')}
Expected Return Date: {rental.expected_return_date.strftime('%Y-%m-%d')}
Days Overdue: {overdue_days}

This equipment is needed for other projects. Please return it immediately to avoid:
- Additional daily charges
- Potential legal action
- Impact on future rental agreements

If you need to discuss an extension, please contact us immediately.

Best regards,
{self.sender_name}
                    """.strip()
                    
                    html_body = f"""
<html>
<body>
<h2 style="color: red;">URGENT NOTICE - Equipment Overdue</h2>
<p>Dear {site.contact_person},</p>
<p>The following equipment is <strong>OVERDUE</strong> and must be returned immediately:</p>
<ul>
<li><strong>Equipment ID:</strong> {rental.equipment.equipment_id}</li>
<li><strong>Equipment Type:</strong> {rental.equipment.type}</li>
<li><strong>Rental Start Date:</strong> {rental.check_out_date.strftime('%Y-%m-%d')}</li>
<li><strong>Expected Return Date:</strong> {rental.expected_return_date.strftime('%Y-%m-%d')}</li>
<li><strong>Days Overdue:</strong> {overdue_days}</li>
</ul>
<p>This equipment is needed for other projects. Please return it immediately to avoid:</p>
<ul>
<li>Additional daily charges</li>
<li>Potential legal action</li>
<li>Impact on future rental agreements</li>
</ul>
<p>If you need to discuss an extension, please contact us immediately.</p>
<p>Best regards,<br>{self.sender_name}</p>
</body>
</html>
                    """.strip()
                    
                    # Send overdue notification
                    if self.send_email(site.contact_person, subject, body, html_body):
                        overdue_notifications_sent += 1
                        
                        # Create alert record
                        alert = models.Alert(
                            rental_id=rental.id,
                            equipment_id=rental.equipment_id,
                            alert_type="overdue",
                            severity="high",
                            title=f"Equipment overdue: {rental.equipment.equipment_id}",
                            description=f"Overdue notification sent to {site.contact_person}. Equipment is {overdue_days} days overdue."
                        )
                        db.add(alert)
                        
                        # Update rental status to overdue
                        rental.status = "overdue"
                        
                    else:
                        failed_notifications += 1
                        
                except Exception as e:
                    logger.error(f"Error sending overdue notification for rental {rental.id}: {e}")
                    failed_notifications += 1
            
            # Commit all changes
            db.commit()
            
            logger.info(f"Overdue notifications completed: {overdue_notifications_sent} sent, {failed_notifications} failed")
            
            return {
                "overdue_notifications_sent": overdue_notifications_sent,
                "failed_notifications": failed_notifications,
                "total_overdue_rentals": len(overdue_rentals)
            }
            
        except Exception as e:
            logger.error(f"Error in send_overdue_notifications: {e}")
            return {"error": str(e)}
    
    def send_equipment_usage_report(self, rental_id: int, usage_data: Dict) -> bool:
        """Send equipment usage report to site contact"""
        try:
            db = next(get_db())
            rental = crud.get_rental(db, rental_id)
            
            if not rental or not rental.site:
                return False
            
            site = rental.site
            equipment = rental.equipment
            
            subject = f"Equipment Usage Report - {equipment.equipment_id}"
            
            body = f"""
Equipment Usage Report

Equipment ID: {equipment.equipment_id}
Equipment Type: {equipment.type}
Site: {site.name}
Report Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}

Usage Summary:
- Engine Hours: {usage_data.get('engine_hours', 0)} hours
- Idle Hours: {usage_data.get('idle_hours', 0)} hours
- Fuel Usage: {usage_data.get('fuel_usage', 0)} liters
- Utilization: {usage_data.get('utilization', 0):.1f}%

Maintenance Status:
- Condition Rating: {usage_data.get('condition_rating', 'N/A')}/10
- Maintenance Required: {'Yes' if usage_data.get('maintenance_required', False) else 'No'}
- Notes: {usage_data.get('maintenance_notes', 'None')}

Best regards,
{self.sender_name}
            """.strip()
            
            return self.send_email(site.contact_person, subject, body)
            
        except Exception as e:
            logger.error(f"Error sending usage report: {e}")
            return False
    
    def send_maintenance_alert(self, equipment_id: int, maintenance_type: str, description: str) -> bool:
        """Send maintenance alert to relevant personnel"""
        try:
            db = next(get_db())
            equipment = crud.get_equipment(db, equipment_id)
            
            if not equipment:
                return False
            
            # Get site contact for maintenance alerts
            site = None
            if equipment.site_id:
                site = crud.get_site_by_site_id(db, equipment.site_id)
            
            subject = f"Maintenance Alert - {equipment.equipment_id}"
            
            body = f"""
Maintenance Alert

Equipment ID: {equipment.equipment_id}
Equipment Type: {equipment.type}
Maintenance Type: {maintenance_type}
Alert Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}

Description:
{description}

Please schedule maintenance as soon as possible.

Best regards,
{self.sender_name}
            """.strip()
            
            # Send to site contact if available, otherwise to admin
            recipient = site.contact_person if site else "admin@company.com"
            
            return self.send_email(recipient, subject, body)
            
        except Exception as e:
            logger.error(f"Error sending maintenance alert: {e}")
            return False
    
    def send_rental_confirmation(self, rental_id: int) -> bool:
        """Send rental confirmation email to site contact"""
        try:
            db = next(get_db())
            rental = crud.get_rental(db, rental_id)
            
            if not rental or not rental.site:
                return False
            
            site = rental.site
            equipment = rental.equipment
            
            subject = f"Rental Confirmation - {equipment.equipment_id}"
            
            body = f"""
Rental Confirmation

Dear {site.contact_person},

Your equipment rental has been confirmed:

Equipment ID: {equipment.equipment_id}
Equipment Type: {equipment.type}
Rental Start Date: {rental.check_out_date.strftime('%Y-%m-%d %H:%M')}
Expected Return Date: {rental.expected_return_date.strftime('%Y-%m-%d') if rental.expected_return_date else 'Not specified'}
Rental Rate: ${rental.rental_rate_per_day}/day (if applicable)

Please note:
- Equipment must be returned in the same condition
- Any damage or issues should be reported immediately
- Return reminders will be sent 7 days before the due date

Thank you for choosing our services.

Best regards,
{self.sender_name}
            """.strip()
            
            html_body = f"""
<html>
<body>
<h2>Rental Confirmation</h2>
<p>Dear {site.contact_person},</p>
<p>Your equipment rental has been confirmed:</p>
<ul>
<li><strong>Equipment ID:</strong> {equipment.equipment_id}</li>
<li><strong>Equipment Type:</strong> {equipment.type}</li>
<li><strong>Rental Start Date:</strong> {rental.check_out_date.strftime('%Y-%m-%d %H:%M')}</li>
<li><strong>Expected Return Date:</strong> {rental.expected_return_date.strftime('%Y-%m-%d') if rental.expected_return_date else 'Not specified'}</li>
<li><strong>Rental Rate:</strong> ${rental.rental_rate_per_day}/day (if applicable)</li>
</ul>
<p>Please note:</p>
<ul>
<li>Equipment must be returned in the same condition</li>
<li>Any damage or issues should be reported immediately</li>
<li>Return reminders will be sent 7 days before the due date</li>
</ul>
<p>Thank you for choosing our services.</p>
<p>Best regards,<br>{self.sender_name}</p>
</body>
</html>
            """.strip()
            
            return self.send_email(site.contact_person, subject, body, html_body)
            
        except Exception as e:
            logger.error(f"Error sending rental confirmation: {e}")
            return False
    
    def send_return_confirmation(self, rental_id: int) -> bool:
        """Send return confirmation email to site contact"""
        try:
            db = next(get_db())
            rental = crud.get_rental(db, rental_id)
            
            if not rental or not rental.site:
                return False
            
            site = rental.site
            equipment = rental.equipment
            
            # Calculate rental duration and cost
            rental_days = (rental.check_in_date - rental.check_out_date).days + 1
            total_cost = rental.total_cost or 0
            
            subject = f"Equipment Return Confirmation - {equipment.equipment_id}"
            
            body = f"""
Return Confirmation

Dear {site.contact_person},

Your equipment has been successfully returned:

Equipment ID: {equipment.equipment_id}
Equipment Type: {equipment.type}
Rental Start Date: {rental.check_out_date.strftime('%Y-%m-%d')}
Return Date: {rental.check_in_date.strftime('%Y-%m-%d')}
Rental Duration: {rental_days} days
Total Cost: ${total_cost:.2f}

Thank you for returning the equipment on time. We appreciate your business.

Best regards,
{self.sender_name}
            """.strip()
            
            html_body = f"""
<html>
<body>
<h2>Return Confirmation</h2>
<p>Dear {site.contact_person},</p>
<p>Your equipment has been successfully returned:</p>
<ul>
<li><strong>Equipment ID:</strong> {equipment.equipment_id}</li>
<li><strong>Equipment Type:</strong> {equipment.type}</li>
<li><strong>Rental Start Date:</strong> {rental.check_out_date.strftime('%Y-%m-%d')}</li>
<li><strong>Return Date:</strong> {rental.check_in_date.strftime('%Y-%m-%d')}</li>
<li><strong>Rental Duration:</strong> {rental_days} days</li>
<li><strong>Total Cost:</strong> ${total_cost:.2f}</li>
</ul>
<p>Thank you for returning the equipment on time. We appreciate your business.</p>
<p>Best regards,<br>{self.sender_name}</p>
</body>
</html>
            """.strip()
            
            return self.send_email(site.contact_person, subject, body, html_body)
            
        except Exception as e:
            logger.error(f"Error sending return confirmation: {e}")
            return False
    
    def send_extension_confirmation(self, rental_id: int, extension_days: int) -> bool:
        """Send rental extension confirmation email to site contact"""
        try:
            db = next(get_db())
            rental = crud.get_rental(db, rental_id)
            
            if not rental or not rental.site:
                return False
            
            site = rental.site
            equipment = rental.equipment
            
            subject = f"Rental Extension Confirmed - {equipment.equipment_id}"
            
            body = f"""
Rental Extension Confirmed

Dear {site.contact_person},

Your rental extension has been confirmed:

Equipment ID: {equipment.equipment_id}
Equipment Type: {equipment.type}
Original Return Date: {rental.check_out_date.strftime('%Y-%m-%d')}
Extended Return Date: {rental.expected_return_date.strftime('%Y-%m-%d') if rental.expected_return_date else 'Not specified'}
Extension Period: {extension_days} days

The equipment will now be available until the new return date. Please ensure it is returned on time.

Best regards,
{self.sender_name}
            """.strip()
            
            html_body = f"""
<html>
<body>
<h2>Rental Extension Confirmed</h2>
<p>Dear {site.contact_person},</p>
<p>Your rental extension has been confirmed:</p>
<ul>
<li><strong>Equipment ID:</strong> {equipment.equipment_id}</li>
<li><strong>Equipment Type:</strong> {equipment.type}</li>
<li><strong>Original Return Date:</strong> {rental.check_out_date.strftime('%Y-%m-%d')}</li>
<li><strong>Extended Return Date:</strong> {rental.expected_return_date.strftime('%Y-%m-%d') if rental.expected_return_date else 'Not specified'}</li>
<li><strong>Extension Period:</strong> {extension_days} days</li>
</ul>
<p>The equipment will now be available until the new return date. Please ensure it is returned on time.</p>
<p>Best regards,<br>{self.sender_name}</p>
</body>
</html>
            """.strip()
            
            return self.send_email(site.contact_person, subject, body, html_body)
            
        except Exception as e:
            logger.error(f"Error sending extension confirmation: {e}")
            return False
    
    def send_single_reminder(self, rental_id: int) -> Dict:
        """Send a single reminder for a specific rental"""
        try:
            db = next(get_db())
            rental = crud.get_rental(db, rental_id)
            
            if not rental or not rental.site:
                return {"success": False, "message": "Rental or site not found"}
            
            site = rental.site
            equipment = rental.equipment
            
            if not site.contact_person:
                return {"success": False, "message": "No contact person for site"}
            
            # Calculate days until return
            if rental.expected_return_date:
                days_until_return = (rental.expected_return_date - datetime.utcnow()).days
            else:
                return {"success": False, "message": "No expected return date set"}
            
            # Prepare email content
            subject = f"Equipment Return Reminder - {equipment.equipment_id}"
            
            body = f"""
Dear {site.contact_person},

This is a friendly reminder that the following equipment is due to be returned:

Equipment ID: {equipment.equipment_id}
Equipment Type: {equipment.type}
Rental Start Date: {rental.check_out_date.strftime('%Y-%m-%d')}
Expected Return Date: {rental.expected_return_date.strftime('%Y-%m-%d')}
Days Until Return: {days_until_return}

Please ensure the equipment is returned on time to avoid any additional charges.

If you need to extend the rental period, please contact us immediately.

Best regards,
{self.sender_name}
            """.strip()
            
            html_body = f"""
<html>
<body>
<h2>Equipment Return Reminder</h2>
<p>Dear {site.contact_person},</p>
<p>This is a friendly reminder that the following equipment is due to be returned:</p>
<ul>
<li><strong>Equipment ID:</strong> {equipment.equipment_id}</li>
<li><strong>Equipment Type:</strong> {equipment.type}</li>
<li><strong>Rental Start Date:</strong> {rental.check_out_date.strftime('%Y-%m-%d')}</li>
<li><strong>Expected Return Date:</strong> {rental.expected_return_date.strftime('%Y-%m-%d')}</li>
<li><strong>Days Until Return:</strong> {days_until_return}</li>
</ul>
<p>Please ensure the equipment is returned on time to avoid any additional charges.</p>
<p>If you need to extend the rental period, please contact us immediately.</p>
<p>Best regards,<br>{self.sender_name}</p>
</body>
</html>
            """.strip()
            
            # Send reminder email
            if self.send_email(site.contact_person, subject, body, html_body):
                # Create alert record
                alert = models.Alert(
                    rental_id=rental.id,
                    equipment_id=rental.equipment_id,
                    alert_type="manual_reminder",
                    severity="medium",
                    title=f"Manual reminder sent for {equipment.equipment_id}",
                    description=f"Manual reminder sent to {site.contact_person} about equipment due in {days_until_return} days"
                )
                db.add(alert)
                db.commit()
                
                return {"success": True, "message": f"Reminder sent successfully to {site.contact_person}"}
            else:
                return {"success": False, "message": "Failed to send reminder email"}
                
        except Exception as e:
            logger.error(f"Error sending single reminder: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
