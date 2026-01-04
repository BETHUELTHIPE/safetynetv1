from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def community_dashboard(request):
    """
    Community dashboard with statistics and data visualization
    """
    context = {
        'total_reports': 0,
        'recent_reports': 0,
        'resolved_reports': 0,
        'reports_by_category': [],
        'upcoming_events': 0,
        'past_events': 0,
        'featured_events': [],
        'active_users': 0,
        'chat_messages': 0,
        'active_alerts': [],
        'safety_score': 50,
        'safety_color': 'info',
        'thirty_day_change': 0,
    }
    
    return render(request, 'dashboard/community_dashboard.html', context)
