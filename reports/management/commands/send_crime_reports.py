from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta

# Assuming you have a CrimeReport model in your reports app
from reports.models import CrimeReport # This line might need adjustment based on your actual model name and location

User = get_user_model()

class Command(BaseCommand):
    help = 'Sends bi-weekly crime reports to all registered users.'

    def handle(self, *args, **options):
        self.stdout.write("Starting bi-weekly crime report email task...")

        # Calculate the date range for the last two weeks
        end_date = timezone.now()
        start_date = end_date - timedelta(weeks=2)

        # Fetch crime reports within the date range
        # You'll need to adjust this query based on your CrimeReport model's fields (e.g., a 'created_at' field)
        recent_reports = CrimeReport.objects.filter(date_reported__range=(start_date, end_date))

        if not recent_reports.exists():
            self.stdout.write("No new crime reports in the last two weeks. Skipping email.")
            return

        # Prepare report data for the email template
        report_data = {
            'start_date': start_date.strftime("%Y-%m-%d"),
            'end_date': end_date.strftime("%Y-%m-%d"),
            'reports': recent_reports,
            'report_count': recent_reports.count()
        }

        # Get all registered users
        users = User.objects.filter(is_active=True)

        if not users.exists():
            self.stdout.write("No active users found to send reports to.")
            return

        for user in users:
            if user.email:
                try:
                    # Render the email content from a template
                    html_content = render_to_string('emails/crime_report_email.html', {'user': user, 'report_data': report_data})
                    text_content = "This is an automated crime report from CPF Crime Reporting System." # Fallback text content

                    email = EmailMultiAlternatives(
                        'Bi-Weekly Crime Report',
                        text_content,
                        'webmaster@yourdomain.com', # Use DEFAULT_FROM_EMAIL from settings.py
                        [user.email]
                    )
                    email.attach_alternative(html_content, "text/html")
                    email.send()
                    self.stdout.write(self.style.SUCCESS(f"Successfully sent report to {user.email}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Failed to send report to {user.email}: {e}"))
            else:
                self.stdout.write(f"User {user.username} has no email address. Skipping.")

        self.stdout.write("Bi-weekly crime report email task completed.")
