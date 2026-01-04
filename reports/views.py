from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test # Added user_passes_test
from django.db.models import Q  # Add Q import for queries
from .forms import CrimeReportForm, CrimeReportUpdateForm # Added CrimeReportUpdateForm
from .models import CrimeReport # Added for fetching crime reports
from django.http import JsonResponse # Added for crime_map_data

# Helper function to check if a user is a Police Officer or Admin
def is_staff_or_admin(user):
    return user.is_authenticated and (hasattr(user, 'profile') and user.profile.role in ['POLICE_OFFICER', 'ADMIN'])

# Create your views here.

@login_required
def submit_report(request):
    if request.method == 'POST':
        form = CrimeReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user # Assign logged-in user as reporter
            report.save()
            return redirect('reports:report_list') # Redirect to the reports list page
    else:
        form = CrimeReportForm()
    return render(request, 'report_form.html', {'form': form})

@login_required
def reports(request):
    # Check if user is admin
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You don't have permission to access all reports.")
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    
    # Start with all reports
    all_crime_reports = CrimeReport.objects.all()
    
    # Apply filters if provided
    if search_query:
        all_crime_reports = all_crime_reports.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) | 
            Q(location__icontains=search_query)
        )
        
    if category_filter:
        all_crime_reports = all_crime_reports.filter(category=category_filter)
        
    if status_filter:
        all_crime_reports = all_crime_reports.filter(status=status_filter)
    
    # Order by newest first
    all_crime_reports = all_crime_reports.order_by('-date_reported')
    
    # Get statistics for the sidebar
    total_reports = CrimeReport.objects.count()
    pending_reports = CrimeReport.objects.filter(status='PENDING').count()
    investigating_reports = CrimeReport.objects.filter(status='UNDER_INVESTIGATION').count()
    resolved_reports = CrimeReport.objects.filter(status__in=['RESOLVED', 'CLOSED']).count()
    
    # Pass all necessary data to the template
    context = {
        'crime_reports': all_crime_reports,
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'investigating_reports': investigating_reports,
        'resolved_reports': resolved_reports,
        'crime_categories': CrimeReport.CRIME_CATEGORIES,
        'status_choices': CrimeReport.STATUS_CHOICES,
    }
    
    return render(request, 'reports.html', context)

@login_required
@user_passes_test(is_staff_or_admin, login_url='/accounts/login/') # Restrict access to staff/admin
def report_detail(request, pk):
    report = get_object_or_404(CrimeReport, pk=pk)
    can_edit_status = False
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        if request.user.profile.role in ['POLICE_OFFICER', 'ADMIN']:
            can_edit_status = True

    if request.method == 'POST' and can_edit_status: # Only allow POST if authorized
        form = CrimeReportUpdateForm(request.POST, instance=report, user=request.user) # Pass user to form
        if form.is_valid():
            form.save()
            return redirect('reports:report_detail', pk=report.pk) # Redirect to the updated report detail page
    else:
        form = CrimeReportUpdateForm(instance=report, user=request.user) # Pass user to form
    return render(request, 'report_detail.html', {'report': report, 'form': form, 'can_edit_status': can_edit_status})

@login_required
def crime_map_data(request):
    reports = CrimeReport.objects.filter(latitude__isnull=False, longitude__isnull=False).values(
        'id', 'title', 'location', 'category', 'status', 'date_reported', 'latitude', 'longitude'
    )
    # Convert datetime objects to string for JSON serialization
    for report in reports:
        report['date_reported'] = report['date_reported'].strftime("%Y-%m-%d %H:%M:%S")
        report['category_display'] = CrimeReport.CRIME_CATEGORIES[next(i for i, (key, val) in enumerate(CrimeReport.CRIME_CATEGORIES) if key == report['category'])][1]
        report['status_display'] = CrimeReport.STATUS_CHOICES[next(i for i, (key, val) in enumerate(CrimeReport.STATUS_CHOICES) if key == report['status'])][1]
    return JsonResponse(list(reports), safe=False)

@login_required
def crime_map_view(request):
    return render(request, 'crime_map.html')
