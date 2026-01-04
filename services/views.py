from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST

from .models import ServiceListing, ServiceReview, ServiceInquiry, ServiceCategory
from .forms import ServiceListingForm, ServiceReviewForm, ServiceInquiryForm

def service_list(request):
    """View to list all service listings"""
    
    # Start with active services only
    services = ServiceListing.objects.filter(status='ACTIVE')
    
    # Handle search
    query = request.GET.get('q')
    if query:
        services = services.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(service_areas__icontains=query) |
            Q(tags__icontains=query)
        )
    
    # Handle category filter
    category_id = request.GET.get('category')
    if category_id:
        services = services.filter(category_id=category_id)
    
    # Handle sort order
    sort = request.GET.get('sort', 'featured')
    if sort == 'newest':
        services = services.order_by('-created_at')
    elif sort == 'oldest':
        services = services.order_by('created_at')
    elif sort == 'rating':
        # Annotate with average rating
        services = services.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating', '-featured')
    else:  # Default to featured
        services = services.order_by('-featured', '-created_at')
    
    # Get all categories for the filter
    categories = ServiceCategory.objects.all()
    
    # Pagination
    paginator = Paginator(services, 12)  # Show 12 services per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'sort': sort,
        'title': 'I Provide Services'
    }
    
    return render(request, 'services/service_list.html', context)


def service_detail(request, pk):
    """View to display a service's details"""
    
    service = get_object_or_404(ServiceListing, pk=pk)
    
    # Increment view count
    service.view_count += 1
    service.save()
    
    # Get reviews for this service
    reviews = service.reviews.all().order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Review form (for authenticated users)
    review_form = None
    if request.user.is_authenticated:
        # Check if user has already reviewed
        user_has_reviewed = ServiceReview.objects.filter(service=service, reviewer=request.user).exists()
        if not user_has_reviewed and request.user != service.provider:
            review_form = ServiceReviewForm()
    
    # Inquiry form (for all users)
    inquiry_form = ServiceInquiryForm()
    
    context = {
        'service': service,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'inquiry_form': inquiry_form,
        'title': service.title
    }
    
    return render(request, 'services/service_detail.html', context)


@login_required
def create_service(request):
    """View for creating a new service listing"""
    
    if request.method == 'POST':
        form = ServiceListingForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.save()
            
            messages.success(request, "Your service listing has been created successfully!")
            return redirect('services:service_detail', pk=service.pk)
    else:
        form = ServiceListingForm()
    
    context = {
        'form': form,
        'title': 'Create Service Listing',
        'button_text': 'Post Service',
        'is_edit': False
    }
    
    return render(request, 'services/service_form.html', context)


@login_required
def edit_service(request, pk):
    """View for editing an existing service listing"""
    
    service = get_object_or_404(ServiceListing, pk=pk)
    
    # Check if user is the provider
    if service.provider != request.user:
        return HttpResponseForbidden("You don't have permission to edit this service.")
    
    if request.method == 'POST':
        form = ServiceListingForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Your service listing has been updated successfully!")
            return redirect('services:service_detail', pk=service.pk)
    else:
        form = ServiceListingForm(instance=service)
    
    context = {
        'form': form,
        'service': service,
        'title': 'Edit Service Listing',
        'button_text': 'Update Service',
        'is_edit': True
    }
    
    return render(request, 'services/service_form.html', context)


@login_required
def delete_service(request, pk):
    """View for deleting a service listing"""
    
    service = get_object_or_404(ServiceListing, pk=pk)
    
    # Check if user is the provider
    if service.provider != request.user:
        return HttpResponseForbidden("You don't have permission to delete this service.")
    
    if request.method == 'POST':
        service.status = 'DISCONTINUED'
        service.save()
        messages.success(request, "Your service listing has been discontinued.")
        return redirect('services:my_services')
    
    context = {
        'service': service,
        'title': 'Delete Service'
    }
    
    return render(request, 'services/service_confirm_delete.html', context)


@login_required
def pause_service(request, pk):
    """View to pause a service listing"""
    
    service = get_object_or_404(ServiceListing, pk=pk)
    
    # Check if user is the provider
    if service.provider != request.user:
        return HttpResponseForbidden("You don't have permission to update this service.")
    
    service.status = 'PAUSED'
    service.save()
    
    messages.success(request, "Your service listing has been paused.")
    return redirect('services:service_detail', pk=service.pk)


@login_required
def activate_service(request, pk):
    """View to activate a paused service listing"""
    
    service = get_object_or_404(ServiceListing, pk=pk)
    
    # Check if user is the provider
    if service.provider != request.user:
        return HttpResponseForbidden("You don't have permission to update this service.")
    
    service.status = 'ACTIVE'
    service.save()
    
    messages.success(request, "Your service listing has been activated.")
    return redirect('services:service_detail', pk=service.pk)


@login_required
def my_services(request):
    """View to display a user's own service listings"""
    
    services = ServiceListing.objects.filter(provider=request.user)
    
    # Filter by status
    status = request.GET.get('status', 'all')
    if status != 'all':
        services = services.filter(status=status.upper())
    
    services = services.order_by('-created_at')
    
    context = {
        'services': services,
        'status': status,
        'title': 'My Services'
    }
    
    return render(request, 'services/my_services.html', context)


@login_required
@require_POST
def add_review(request, pk):
    """View to add a review to a service"""
    
    service = get_object_or_404(ServiceListing, pk=pk)
    
    # Don't allow reviewing your own service
    if service.provider == request.user:
        messages.error(request, "You cannot review your own service.")
        return redirect('services:service_detail', pk=pk)
    
    # Check if user has already reviewed
    if ServiceReview.objects.filter(service=service, reviewer=request.user).exists():
        messages.error(request, "You have already reviewed this service.")
        return redirect('services:service_detail', pk=pk)
    
    form = ServiceReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.service = service
        review.reviewer = request.user
        review.save()
        
        messages.success(request, "Thank you for your review!")
    else:
        messages.error(request, "There was an error with your review. Please try again.")
    
    return redirect('services:service_detail', pk=pk)


@login_required
def my_reviews(request):
    """View to display reviews written by the user"""
    
    reviews = ServiceReview.objects.filter(reviewer=request.user).order_by('-created_at')
    
    context = {
        'reviews': reviews,
        'title': 'My Reviews'
    }
    
    return render(request, 'services/my_reviews.html', context)


def send_inquiry(request, pk):
    """View to send an inquiry about a service"""
    
    service = get_object_or_404(ServiceListing, pk=pk)
    
    if request.method == 'POST':
        form = ServiceInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.service = service
            
            # Associate with user if logged in
            if request.user.is_authenticated:
                inquiry.user = request.user
                # Pre-fill from user profile if available
                if not inquiry.name and (request.user.first_name or request.user.last_name):
                    inquiry.name = f"{request.user.first_name} {request.user.last_name}".strip()
                if not inquiry.email and request.user.email:
                    inquiry.email = request.user.email
            
            inquiry.save()
            
            messages.success(request, "Your inquiry has been sent to the service provider!")
            return redirect('services:service_detail', pk=pk)
        else:
            messages.error(request, "Please correct the errors in your inquiry form.")
    else:
        form = ServiceInquiryForm()
    
    context = {
        'service': service,
        'form': form,
        'title': f'Contact about {service.title}'
    }
    
    return render(request, 'services/send_inquiry.html', context)


@login_required
def my_inquiries(request):
    """View to display inquiries about the user's services"""
    
    inquiries = ServiceInquiry.objects.filter(service__provider=request.user).order_by('-created_at')
    
    context = {
        'inquiries': inquiries,
        'title': 'Service Inquiries'
    }
    
    return render(request, 'services/my_inquiries.html', context)


@login_required
def mark_inquiry_read(request, pk):
    """View to mark an inquiry as read"""
    
    inquiry = get_object_or_404(ServiceInquiry, pk=pk)
    
    # Check if user is the service provider
    if inquiry.service.provider != request.user:
        return HttpResponseForbidden("You don't have permission to update this inquiry.")
    
    inquiry.read = True
    inquiry.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('services:my_inquiries')


def category_services(request, category_id):
    """View to show services in a specific category"""
    
    category = get_object_or_404(ServiceCategory, pk=category_id)
    services = ServiceListing.objects.filter(category=category, status='ACTIVE').order_by('-featured', '-created_at')
    
    # Pagination
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'title': f'{category.name} Services'
    }
    
    return render(request, 'services/category_services.html', context)
