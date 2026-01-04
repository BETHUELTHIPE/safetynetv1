from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

def home(request):
    """Home page for the Kings Park Community Police Forum."""
    return render(request, 'home.html')

def crime_reporting_dashboard(request):
    """Public crime reporting dashboard for all users."""
    return render(request, 'crime_reporting_dashboard.html', {
        'title': 'Report a Crime'
    })

@login_required
def admin_dashboard(request):
    """Admin dashboard for CPF members and administrators only."""
    # Check if user is admin or CPF member
    if not (request.user.is_staff or request.user.groups.filter(name='CPF_Members').exists()):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You don't have permission to access the admin dashboard.")
    
    return render(request, 'dashboard.html', {
        'title': 'Admin Dashboard'
    })

@login_required
def dashboard_view(request):
    """Dashboard view for registered users (redirects to appropriate dashboard)."""
    # Check if user is admin or CPF member
    if request.user.is_staff or request.user.groups.filter(name='CPF_Members').exists():
        return admin_dashboard(request)
    else:
        return crime_reporting_dashboard(request)

def about(request):
    """About Us page for Kings Park, Kwamhlanga Community Police Forum."""
    return render(request, 'about.html', {
        'title': 'About Us'
    })

def contact(request):
    """Contact Us page for Kings Park, Kwamhlanga Community Police Forum."""
    return render(request, 'contact.html', {
        'title': 'Contact Us'
    })

def handler404(request, exception):
    """Custom 404 error page."""
    return render(request, '404.html', status=404)

def handler500(request):
    """Custom 500 error page."""
    return render(request, '500.html', status=500)

def handler403(request, exception):
    """Custom 403 error page."""
    return render(request, '403.html', status=403)

def terms_and_conditions(request):
    """Terms and conditions page."""
    return render(request, 'terms.html', {
        'title': 'Terms and Conditions'
    })

def safety_tips(request):
    """Safety tips page."""
    return render(request, 'safety_tips.html', {
        'title': 'Safety Tips'
    })

def emergency_contacts(request):
    """Emergency contacts page."""
    return render(request, 'emergency_contacts.html', {
        'title': 'Emergency Contacts'
    })

def privacy_policy(request):
    """Privacy policy page."""
    return render(request, 'privacy.html', {
        'title': 'Privacy Policy'
    })
