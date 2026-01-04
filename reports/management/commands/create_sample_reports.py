from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from reports.models import CrimeReport

class Command(BaseCommand):
    help = 'Create sample crime reports for testing'

    def handle(self, *args, **options):
        # Sample data
        sample_titles = [
            "Vehicle Break-in on Main Street",
            "Suspicious Activity Near Park",
            "Shoplifting at Local Store",
            "Vandalism at Community Center",
            "Assault Outside Nightclub",
            "Burglary on Oak Avenue",
            "Theft from Vehicle",
            "Drug Activity Reported",
            "Cybercrime - Online Fraud",
            "Robbery at Gas Station"
        ]

        sample_descriptions = [
            "Car window smashed, laptop and phone stolen from back seat. Occurred around 10 PM.",
            "Group of individuals loitering, acting suspiciously near children's playground after hours.",
            "Individual caught stealing items from store shelf. Security cameras captured incident.",
            "Graffiti spray-painted on community building walls. Needs immediate cleanup.",
            "Physical altercation resulting in minor injuries. Police called to scene.",
            "Home broken into through back window. Electronics and jewelry missing.",
            "Unlocked vehicle entered, wallet and sunglasses stolen from dashboard.",
            "Suspicious drug dealing activity observed in vacant lot area.",
            "Email phishing scam targeting elderly residents. Multiple victims identified.",
            "Armed robbery at gas station, suspect fled on foot with cash register contents."
        ]

        sample_locations = [
            "123 Main Street, Kings Park",
            "Kings Park Community Park",
            "Spar Supermarket, Kings Park",
            "Community Center, B107 Kings Park Village",
            "Nightclub, Central Avenue",
            "456 Oak Avenue, Kings Park",
            "Parking Lot - Shopping Center",
            "Vacant Lot - Corner of 5th Street",
            "Various online platforms",
            "Shell Gas Station, Highway Intersection"
        ]

        # Create sample users if they don't exist
        users = []
        for i in range(10):
            username = f"sampleuser{i+1}"
            email = f"sample{i+1}@example.com"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Sample{i+1}',
                    'last_name': f'User{i+1}'
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f"Created user: {username}")
            
            users.append(user)

        # Create sample crime reports
        categories = ['THEFT', 'ASSAULT', 'VANDALISM', 'BURGLARY', 'ROBBERY', 'DRUG_OFFENSE', 'CYBERCRIME', 'OTHER']
        statuses = ['PENDING', 'UNDER_INVESTIGATION', 'RESOLVED', 'CLOSED']
        
        created_reports = 0
        for i in range(10):
            # Random date within last 30 days
            days_ago = random.randint(0, 30)
            report_date = timezone.now() - timedelta(days=days_ago)
            
            report = CrimeReport.objects.create(
                title=sample_titles[i],
                description=sample_descriptions[i],
                location=sample_locations[i],
                category=random.choice(categories),
                status=random.choice(statuses),
                date_reported=report_date,
                latitude=-25.53237 + random.uniform(-0.01, 0.01),  # Kings Park area
                longitude=29.044827 + random.uniform(-0.01, 0.01),
                reporter=users[i]
            )
            
            created_reports += 1
            self.stdout.write(f"Created report {i+1}: {report.title}")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_reports} sample crime reports")
        )
