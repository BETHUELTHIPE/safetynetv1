from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from reports.models import CrimeReport
from kingspark_events.models import Event
from community_alerts.models import Alert
from community_chat.models import ChatMessage
from accounts.models import Profile

@login_required
def community_dashboard(request):
    """
    Community dashboard with statistics and data visualization
    """
    # Get statistics for the last 30 days
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # Crime reports stats
    total_reports = CrimeReport.objects.count()
    recent_reports = CrimeReport.objects.filter(date_reported__gte=thirty_days_ago).count()
    resolved_reports = CrimeReport.objects.filter(status__in=['RESOLVED', 'CLOSED']).count()
    reports_by_category = CrimeReport.objects.values('category').annotate(
        count=Count('category')).order_by('-count')[:5]
    
    # Events stats
    upcoming_events = Event.objects.filter(start_date__gte=now).count()
    past_events = Event.objects.filter(start_date__lt=now).count()
    featured_events = Event.objects.filter(is_featured=True, start_date__gte=now)[:3]
    
    # Community engagement
    active_users = Profile.objects.count()
    chat_messages = ChatMessage.objects.filter(timestamp__gte=thirty_days_ago).count()
    
    # Active alerts
    active_alerts = Alert.objects.filter(
        is_approved=True, 
        Q(expires_at__isnull=True) | Q(expires_at__gt=now)
    ).order_by('-created_at')[:5]
    
    # Safety score calculation (simplified example)
    resolved_percentage = (resolved_reports / total_reports * 100) if total_reports > 0 else 0
    safety_score = min(100, max(0, 40 + resolved_percentage * 0.6)) # Scale between 40-100
    
    context = {
        'total_reports': total_reports,
        'recent_reports': recent_reports,
        'resolved_reports': resolved_reports,
        'reports_by_category': reports_by_category,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'featured_events': featured_events,
        'active_users': active_users,
        'chat_messages': chat_messages,
        'active_alerts': active_alerts,
        'safety_score': int(safety_score),
        'safety_color': get_safety_color(safety_score),
        'thirty_day_change': calculate_change(thirty_days_ago),
    }
    
    return render(request, 'dashboard/community_dashboard.html', context)

def get_safety_color(score):
    """Return a color based on safety score"""
    if score >= 80:
        return 'success'
    elif score >= 60:
        return 'info'
    elif score >= 40:
        return 'warning'
    else:
        return 'danger'

def calculate_change(thirty_days_ago):
    """Calculate change in crime reports compared to previous period"""
    current_period = CrimeReport.objects.filter(date_reported__gte=thirty_days_ago).count()
    previous_start = thirty_days_ago - timedelta(days=30)
    previous_period = CrimeReport.objects.filter(
        date_reported__gte=previous_start,
        date_reported__lt=thirty_days_ago
    ).count()
    
    if previous_period == 0:
        if current_period == 0:
            return 0
        return 100 # Arbitrary large increase
    
    change = ((current_period - previous_period) / previous_period) * 100
    return round(change, 1)
