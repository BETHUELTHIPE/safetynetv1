from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class CrimeReport(models.Model):
    CRIME_CATEGORIES = [
        ('THEFT', 'Theft'),
        ('ASSAULT', 'Assault'),
        ('VANDALISM', 'Vandalism'),
        ('BURGLARY', 'Burglary'),
        ('HOMICIDE', 'Homicide'),
        ('ROBBERY', 'Robbery'),
        ('DRUG_OFFENSE', 'Drug Offense'),
        ('CYBERCRIME', 'Cybercrime'),
        ('OTHER', 'Other'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CRIME_CATEGORIES, default='OTHER')
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('UNDER_INVESTIGATION', 'Under Investigation'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
        ('REJECTED', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    date_reported = models.DateTimeField(default=timezone.now)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title
