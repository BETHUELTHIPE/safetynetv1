from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
from django.http import HttpResponseForbidden

from .models import BusinessService, ServiceApplication
from .forms import BusinessServiceForm

def job_list(request):
    """View to list all business services."""
    # Get all active services
    services = BusinessService.objects.filter(status='OPEN')
    
    # Handle search
    query = request.GET.get('q')
    if query:
        services = services.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(category__icontains=query)
        )
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        services = services.filter(category=category)
    
    # Pagination
    paginator = Paginator(services, 10)  # 10 services per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique categories for filtering
    categories = BusinessService.objects.values_list('category', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'title': 'Business Services'
    }
    
    return render(request, 'piecejobs/job_list.html', context)

def job_detail(request, pk):
    """View to show service details."""
    service = get_object_or_404(BusinessService, pk=pk)
    
    # Check if the current user has applied
    user_has_applied = False
    if request.user.is_authenticated:
        user_has_applied = ServiceApplication.objects.filter(service=service, applicant=request.user).exists()
    
    context = {
        'service': service,
        'user_has_applied': user_has_applied,
        'title': service.title
    }
    
    return render(request, 'piecejobs/job_detail.html', context)

@login_required
def create_job(request):
    """View to create a new business service."""
    if request.method == 'POST':
        form = BusinessServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.poster = request.user
            service.save()
            
            messages.success(request, "Your service has been posted successfully!")
            return redirect('business_services:service_detail', pk=service.pk)
    else:
        form = BusinessServiceForm()
    
    context = {
        'form': form,
        'title': 'Post a Business Service',
        'button_text': 'Post Service',
        'is_edit': False
    }
    
    return render(request, 'piecejobs/job_form.html', context)

@login_required
def edit_job(request, pk):
    """View to edit an existing business service."""
    service = get_object_or_404(BusinessService, pk=pk)
    
    # Only allow the service poster to edit
    if service.poster != request.user:
        return HttpResponseForbidden("You don't have permission to edit this service.")
    
    if request.method == 'POST':
        form = BusinessServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Service updated successfully!")
            return redirect('business_services:service_detail', pk=service.pk)
    else:
        form = BusinessServiceForm(instance=service)
    
    context = {
        'form': form,
        'service': service,
        'title': 'Edit Business Service',
        'button_text': 'Update Service',
        'is_edit': True
    }
    
    return render(request, 'piecejobs/job_form.html', context)

@login_required
def delete_job(request, pk):
    """View to delete a business service."""
    service = get_object_or_404(BusinessService, pk=pk)
    
    # Only allow the service poster to delete
    if service.poster != request.user:
        return HttpResponseForbidden("You don't have permission to delete this service.")
    
    if request.method == 'POST':
        service.status = 'CANCELLED'
        service.save()
        messages.success(request, "Service deleted successfully!")
        return redirect('my_services')
    
    context = {
        'service': service,
        'title': 'Delete Service'
    }
    
    return render(request, 'piecejobs/job_confirm_delete.html', context)

@login_required
def my_jobs(request):
    """View to show services posted by the current user."""
    services = BusinessService.objects.filter(poster=request.user)
    
    context = {
        'services': services,
        'title': 'My Services'
    }
    
    return render(request, 'piecejobs/my_jobs.html', context)

@login_required
def apply_job(request, pk):
    """View to apply for a service."""
    service = get_object_or_404(BusinessService, pk=pk)
    
    # Can't apply to your own service
    if service.poster == request.user:
        messages.error(request, "You cannot apply to your own service posting.")
        return redirect('business_services:service_detail', pk=pk)
    
    # Check if already applied
    if ServiceApplication.objects.filter(service=service, applicant=request.user).exists():
        messages.warning(request, "You have already applied for this service.")
        return redirect('business_services:service_detail', pk=pk)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        contact_number = request.POST.get('contact_number')
        
        if not message or not contact_number:
            messages.error(request, "Both message and contact number are required.")
            return redirect('business_services:apply_service', pk=pk)
        
        ServiceApplication.objects.create(
            service=service,
            applicant=request.user,
            message=message,
            contact_number=contact_number
        )
        
        messages.success(request, "Your application has been submitted successfully!")
        return redirect('business_services:service_detail', pk=pk)
    
    context = {
        'service': service,
        'title': 'Apply for Service'
    }
    
    return render(request, 'piecejobs/apply_job.html', context)

@login_required
def my_applications(request):
    """View to show applications made by the current user."""
    applications = ServiceApplication.objects.filter(applicant=request.user)
    
    context = {
        'applications': applications,
        'title': 'My Applications'
    }
    
    return render(request, 'piecejobs/my_applications.html', context)

@login_required
def job_applications(request, pk):
    """View to show applications for a service."""
    service = get_object_or_404(BusinessService, pk=pk)
    
    # Only allow the service poster to view applications
    if service.poster != request.user:
        return HttpResponseForbidden("You don't have permission to view applications for this service.")
    
    applications = ServiceApplication.objects.filter(service=service)
    
    context = {
        'service': service,
        'applications': applications,
        'title': f'Applications for {service.title}'
    }
    
    return render(request, 'piecejobs/job_applications.html', context)
