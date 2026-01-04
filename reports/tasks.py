import os
import logging
from datetime import datetime, timedelta
from celery import shared_task
from twilio.rest import Client
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from .report_generator import MonthlyReportGenerator

logger = logging.getLogger(__name__)

@shared_task
def send_sms_alert(to_phone_number, message):
    """Send SMS alert using Twilio"""
    # Ensure Twilio credentials are set
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        logger.warning("Twilio credentials are not set. Skipping SMS.")
        return

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    try:
        message = client.messages.create(
            to=to_phone_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            body=message
        )
        logger.info(f"SMS sent to {to_phone_number}: {message.sid}")
    except Exception as e:
        logger.error(f"Error sending SMS to {to_phone_number}: {e}")

@shared_task
def generate_monthly_crime_report():
    """Generate monthly crime report PDF"""
    logger.info("Starting monthly crime report generation")
    
    try:
        # Generate report for the previous month
        generator = MonthlyReportGenerator()
        pdf_path = generator.generate_pdf()
        
        logger.info(f"Crime report generated successfully: {pdf_path}")
        return pdf_path
    except Exception as e:
        logger.error(f"Error generating monthly crime report: {e}")
        return None

@shared_task
def send_monthly_report_email(pdf_path=None):
    """Send monthly crime report to all registered users"""
    if pdf_path is None:
        pdf_path = generate_monthly_crime_report()
        
    if not pdf_path or not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return
    
    # Get month and year for email subject
    now = datetime.now()
    month_name = (now.replace(day=1) - timedelta(days=1)).strftime("%B")
    year = (now.replace(day=1) - timedelta(days=1)).year
    
    try:
        # Get all users with email notifications enabled
        users = User.objects.filter(profile__email_notifications=True)
        
        if not users:
            logger.info("No users found with email notifications enabled")
            return
        
        # Generate email subject and content
        subject = f"KingsPark Crime Report - {month_name} {year}"
        
        # Get connection
        connection = get_connection()
        connection.open()
        
        # Send emails in batches
        batch_size = 50
        total_users = users.count()
        success_count = 0
        
        for i in range(0, total_users, batch_size):
            batch_users = users[i:i+batch_size]
            emails = []
            
            for user in batch_users:
                # Create email content personalized for each user
                html_content = render_to_string('reports/email/monthly_report.html', {
                    'user': user,
                    'month': month_name,
                    'year': year,
                })
                
                email = EmailMessage(
                    subject=subject,
                    body=html_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                    connection=connection,
                )
                email.content_subtype = "html"  # Set content type to HTML
                
                # Attach the PDF report
                with open(pdf_path, 'rb') as f:
                    email.attach(f"KingsPark_Crime_Report_{month_name}_{year}.pdf", f.read(), 'application/pdf')
                
                emails.append(email)
            
            # Send all emails in this batch
            sent_count = 0
            for email in emails:
                try:
                    email.send()
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error sending email to {email.to[0]}: {e}")
            
            success_count += sent_count
            logger.info(f"Sent {sent_count}/{len(emails)} emails in batch {i//batch_size + 1}")
        
        connection.close()
        logger.info(f"Successfully sent {success_count}/{total_users} monthly crime report emails")
        
    except Exception as e:
        logger.error(f"Error in send_monthly_report_email: {e}")

