# Smart Rental Tracking - Email Notification System

This system automatically sends email reminders to operators 7 days before their equipment rental is due for return.

## Features

- 📧 Automated email notifications
- ⏰ Scheduled daily checks at 9:00 AM
- 🎨 Professional HTML email templates
- 📊 Notification logging and alerts
- 🔧 Configurable email settings
- 🧪 Testing tools included

## Quick Setup

### 1. Install Required Packages

The required packages should already be installed:

- `python-dotenv` - For environment variables
- `schedule` - For task scheduling
- `smtplib` - For sending emails (built-in)

### 2. Configure Email Settings

1. Copy the example configuration:

   ```powershell
   copy .env.example .env
   ```

2. Edit `.env` file with your email settings:
   ```
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_ADDRESS=your-company-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   COMPANY_NAME=Your Company Name
   ```

### 3. For Gmail Setup:

1. Enable 2-factor authentication on your Google account
2. Go to Google Account settings → Security → 2-Step Verification → App passwords
3. Generate an app password for "Mail"
4. Use this app password in the `.env` file (not your regular password)

## Usage

### Test the System

Run the test script to verify everything works:

```powershell
cd backend
python test_notifications.py
```

### Send Manual Reminders

Run reminders immediately:

```powershell
cd backend
python reminder_service.py
```

### Start Automated Scheduler

Run the automated daily scheduler:

```powershell
cd backend
python scheduler.py
```

The scheduler will:

- Run daily at 9:00 AM
- Check for rentals due in 7 days
- Send email reminders automatically
- Log all notifications in the database

## Email Template

The system sends professional HTML emails with:

- **Equipment details** (ID, type, model)
- **Rental information** (check-out date, due date, site)
- **Return instructions** and location
- **Contact information** for extensions
- **Important reminders** (cleaning, maintenance, accessories)

## System Integration

### Database Logging

- All sent notifications are logged as alerts in the database
- Failed notifications create system alerts for monitoring
- Check the alerts table for notification history

### API Integration

The notification service integrates with the existing FastAPI backend:

- Uses the same database models and CRUD operations
- Follows the same data validation schemas
- Can be monitored through the API dashboard

## Monitoring

### Check Notification Status

1. **Via API**: Visit `http://localhost:8000/alerts` to see notification logs
2. **Via Database**: Query the alerts table for recent notifications
3. **Via Logs**: Check console output for real-time status

### Troubleshooting

Common issues and solutions:

1. **"Email not configured" warning**:

   - Update `.env` file with your actual email credentials

2. **"Authentication failed" error**:

   - For Gmail: Ensure you're using an app password, not your regular password
   - For other providers: Check SMTP settings and credentials

3. **"No rentals due" message**:

   - This is normal if no equipment returns are due in 7 days
   - Test with mock data using `test_notifications.py`

4. **Import errors**:
   - Ensure you're running from the `backend` directory
   - Check that all required packages are installed

## Customization

### Change Reminder Timing

Edit `scheduler.py` to change when reminders are sent:

```python
# Change this line to set different time
schedule.every().day.at("09:00").do(job)  # 9:00 AM
schedule.every().day.at("14:30").do(job)  # 2:30 PM
```

### Add Multiple Reminder Days

Edit `reminder_service.py` to send reminders at different intervals:

```python
# In run_daily_reminders() function, add:
reminder_service.send_reminder_notifications(days_ahead=7)  # 7 days
reminder_service.send_reminder_notifications(days_ahead=3)  # 3 days
reminder_service.send_reminder_notifications(days_ahead=1)  # 1 day
```

### Customize Email Template

Edit the `create_reminder_email_body()` method in `EmailService` class to modify:

- Email styling and layout
- Company branding
- Additional information
- Contact details

## Production Deployment

For production use:

1. **Use a dedicated email service** (SendGrid, AWS SES, etc.)
2. **Set up proper logging** with file outputs
3. **Use a process manager** (PM2, supervisor) for the scheduler
4. **Monitor email delivery** rates and failures
5. **Set up database backups** for notification logs

## Security Notes

- Never commit `.env` file to version control
- Use app passwords instead of regular passwords
- Limit email account permissions to sending only
- Monitor for suspicious email activity
- Use environment-specific configurations

## Support

For issues or questions:

1. Check the console output for error messages
2. Verify email configuration in `.env`
3. Test with `test_notifications.py`
4. Check database connectivity
5. Verify operator email addresses in database
