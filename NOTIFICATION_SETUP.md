# Email Notification Setup Guide

## Overview

The Smart Rental Tracker includes an automated notification system that sends email reminders to operators before equipment return dates and alerts for overdue rentals.

## Features

- 📧 **Return Reminders**: Automatically sends emails 7 days before equipment is due back
- ⚠️ **Overdue Alerts**: Sends urgent notifications for equipment that's past its return date
- 📊 **Dashboard Integration**: API endpoints to view upcoming and overdue rentals
- ⏰ **Scheduled Automation**: Can run automatically on a schedule
- 🧪 **Testing Tools**: Built-in email configuration testing

## Setup Instructions

### 1. Configure Email Settings

Edit the `.env` file in the `backend/app/` directory:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=Smart Rental Tracker <your_email@gmail.com>

# Notification Settings
NOTIFICATION_DAYS_AHEAD=7
```

### 2. Gmail Setup (Recommended)

If using Gmail:

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Select app: "Mail"
   - Copy the 16-character password
3. **Use App Password** in SMTP_PASSWORD (not your regular password)

### 3. Other Email Providers

#### Outlook/Hotmail

```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your_email@outlook.com
SMTP_PASSWORD=your_password
```

#### Yahoo Mail

```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your_email@yahoo.com
SMTP_PASSWORD=your_app_password
```

## Testing the System

### 1. Test Email Configuration

```bash
cd backend/app
python test_notifications.py
```

### 2. Test via API

```bash
curl -X POST "http://localhost:8000/notifications/test-email-config"
```

### 3. Manual Notification Run

```bash
curl -X POST "http://localhost:8000/notifications/run-all"
```

## API Endpoints

### Get Upcoming Returns

```http
GET /notifications/upcoming-returns
```

Returns equipment rentals due within the notification window.

### Get Overdue Rentals

```http
GET /notifications/overdue-rentals
```

Returns equipment rentals that are past their return date.

### Send Return Reminders

```http
POST /notifications/send-return-reminders
```

Sends email reminders for upcoming returns.

### Send Overdue Notifications

```http
POST /notifications/send-overdue-notifications
```

Sends email notifications for overdue rentals.

### Test Email Configuration

```http
POST /notifications/test-email-config
```

Tests the email configuration without sending emails.

### Run All Notifications

```http
POST /notifications/run-all
```

Runs both return reminders and overdue notifications.

## Automation

### Start Scheduler

To run notifications automatically:

```bash
cd backend/app
python scheduler.py
```

The scheduler runs:

- Return reminders: Daily at 9:00 AM
- Overdue notifications: Daily at 2:00 PM
- Full check: Daily at 6:00 PM

### Schedule Options

```bash
# Test configuration only
python scheduler.py --config-test

# Run immediate test
python scheduler.py --test

# Start scheduled service
python scheduler.py
```

## Email Templates

### Return Reminder Email

Sent 7 days before equipment is due:

- Equipment details (name, type, serial number)
- Site information
- Return date
- Contact information

### Overdue Notification Email

Sent for equipment past return date:

- Equipment details
- Days overdue
- Estimated late fees
- Urgent action required
- Contact information

## Troubleshooting

### Common Issues

**1. Authentication Failed**

- Check SMTP username/password
- For Gmail, use App Password instead of regular password
- Ensure 2FA is enabled for Gmail

**2. Connection Refused**

- Verify SMTP server and port
- Check firewall settings
- Ensure internet connectivity

**3. No Emails Sent**

- Verify operator email addresses are set in database
- Check notification window (default 7 days)
- Ensure rentals exist with appropriate dates

### Debug Steps

1. **Test Email Config**:

   ```bash
   python test_notifications.py
   ```

2. **Check Database**:

   ```bash
   python -c "from notification_service import NotificationService; ns = NotificationService(); print(f'Upcoming: {len(ns.get_upcoming_returns())}'); print(f'Overdue: {len(ns.get_overdue_rentals())}')"
   ```

3. **View Logs**:
   ```bash
   tail -f notifications.log
   tail -f scheduler.log
   ```

## Security Notes

- Never commit `.env` file to version control
- Use app passwords instead of regular passwords
- Regularly rotate email credentials
- Monitor email logs for suspicious activity

## Customization

### Modify Notification Timing

Change `NOTIFICATION_DAYS_AHEAD` in `.env` file:

```env
NOTIFICATION_DAYS_AHEAD=5  # Send reminders 5 days ahead
```

### Customize Email Templates

Edit the email body in `notification_service.py`:

- `create_return_reminder_email()` function
- `create_overdue_email()` function

### Add Schedule Times

Modify `scheduler.py` to add more notification times:

```python
schedule.every().day.at("12:00").do(run_notifications)
```
