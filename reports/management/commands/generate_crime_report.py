from django.core.management.base import BaseCommand
from reports.tasks import generate_monthly_crime_report, send_monthly_report_email
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate and optionally send the monthly crime report'

    def add_arguments(self, parser):
        parser.add_argument(
            '--send',
            action='store_true',
            help='Also send the report by email to all users'
        )
        
        parser.add_argument(
            '--month',
            type=int,
            default=None,
            help='Month to generate report for (1-12)'
        )
        
        parser.add_argument(
            '--year',
            type=int,
            default=None,
            help='Year to generate report for'
        )

    def handle(self, *args, **options):
        send_email = options['send']
        month = options['month']
        year = options['year']
        
        self.stdout.write(self.style.NOTICE('Starting crime report generation...'))
        
        try:
            if month and year:
                self.stdout.write(self.style.NOTICE(f'Generating report for {month}/{year}'))
                from reports.report_generator import MonthlyReportGenerator
                generator = MonthlyReportGenerator(month=month, year=year)
                pdf_path = generator.generate_pdf()
            else:
                self.stdout.write(self.style.NOTICE('Generating report for previous month'))
                pdf_path = generate_monthly_crime_report()
                
            if pdf_path:
                self.stdout.write(self.style.SUCCESS(f'Report successfully generated: {pdf_path}'))
                
                if send_email:
                    self.stdout.write(self.style.NOTICE('Sending report by email...'))
                    send_monthly_report_email(pdf_path)
                    self.stdout.write(self.style.SUCCESS('Emails sent successfully'))
            else:
                self.stdout.write(self.style.ERROR('Failed to generate report'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
