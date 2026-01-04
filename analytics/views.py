from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncDate
from reports.models import CrimeReport # Assuming CrimeReport model is in reports app

# Create your views here.

@login_required
def crime_category_distribution(request):
    # Check if user is admin
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You don't have permission to access analytics.")
    
    category_data = CrimeReport.objects.values('category').annotate(count=Count('category')).order_by('category')
    labels = [item['category'] for item in category_data]
    data = [item['count'] for item in category_data]
    return JsonResponse({'labels': labels, 'data': data})

@login_required
def crime_trends_monthly(request):
    # Check if user is admin
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You don't have permission to access analytics.")
    
    monthly_data = CrimeReport.objects.annotate(month=TruncMonth('date_reported')).values('month').annotate(count=Count('id')).order_by('month')
    labels = [item['month'].strftime('%Y-%m') for item in monthly_data]
    data = [item['count'] for item in monthly_data]
    return JsonResponse({'labels': labels, 'data': data})

@login_required
def crime_trends_daily(request):
    # Check if user is admin
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You don't have permission to access analytics.")
    
    daily_data = CrimeReport.objects.annotate(date=TruncDate('date_reported')).values('date').annotate(count=Count('id')).order_by('date')
    labels = [item['date'].strftime('%Y-%m-%d') for item in daily_data]
    data = [item['count'] for item in daily_data]
    return JsonResponse({'labels': labels, 'data': data})

@login_required
def analytics_dashboard_view(request):
    # Check if user is admin
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You don't have permission to access analytics.")
    
    return render(request, 'analytics_dashboard.html')
