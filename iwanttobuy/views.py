from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.utils import timezone

from .models import BuyRequest, BuyRequestResponse
from .forms import BuyRequestForm, BuyRequestResponseForm

def request_list(request):
    """View to list all buy requests"""
    
    # Start with active requests only
    buy_requests = BuyRequest.objects.filter(status='ACTIVE')
    
    # Handle search
    query = request.GET.get('q')
    if query:
        buy_requests = buy_requests.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(tags__icontains=query)
        )
    
    # Handle category filter
    category = request.GET.get('category')
    if category:
        buy_requests = buy_requests.filter(category=category)
    
    # Handle urgency filter
    urgency = request.GET.get('urgency')
    if urgency:
        buy_requests = buy_requests.filter(urgency=urgency)
    
    # Handle sort order
    sort = request.GET.get('sort', 'newest')
    if sort == 'urgency':
        # Order by urgency level (HIGH to LOW)
        buy_requests = buy_requests.order_by(
            # Custom order for urgency levels
            # This puts URGENT first, then HIGH, MEDIUM, LOW
            # We use Case to define the custom order
            models.Case(
                models.When(urgency='URGENT', then=1),
                models.When(urgency='HIGH', then=2),
                models.When(urgency='MEDIUM', then=3),
                models.When(urgency='LOW', then=4),
                default=5,
                output_field=models.IntegerField()
            ),
            '-created_at'  # Secondary sort by creation date
        )
    elif sort == 'oldest':
        buy_requests = buy_requests.order_by('created_at')
    else:  # Default to newest
        buy_requests = buy_requests.order_by('-created_at')
    
    # Get categories for filtering
    categories = BuyRequest.objects.filter(status='ACTIVE').values_list(
        'category', flat=True
    ).distinct()
    
    # Pagination
    paginator = Paginator(buy_requests, 12)  # Show 12 requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'selected_urgency': urgency,
        'sort': sort,
        'urgency_choices': BuyRequest.URGENCY_CHOICES,
        'title': 'I Want to Buy'
    }
    
    return render(request, 'iwanttobuy/request_list.html', context)


def request_detail(request, pk):
    """View to display a buy request's details"""
    
    buy_request = get_object_or_404(BuyRequest, pk=pk)
    
    # Increment view count
    buy_request.view_count += 1
    buy_request.save()
    
    # Get responses if user is the requester
    responses = None
    if request.user.is_authenticated and request.user == buy_request.requester:
        responses = buy_request.responses.all().order_by('-created_at')
    
    # Response form
    form = BuyRequestResponseForm()
    
    context = {
        'buy_request': buy_request,
        'responses': responses,
        'form': form,
        'title': buy_request.title
    }
    
    return render(request, 'iwanttobuy/request_detail.html', context)


@login_required
def create_request(request):
    """View for creating a new buy request"""
    
    if request.method == 'POST':
        form = BuyRequestForm(request.POST, request.FILES)
        if form.is_valid():
            buy_request = form.save(commit=False)
            buy_request.requester = request.user
            buy_request.save()
            
            messages.success(request, "Your buy request has been posted successfully!")
            return redirect('iwanttobuy:request_detail', pk=buy_request.pk)
    else:
        form = BuyRequestForm()
    
    context = {
        'form': form,
        'title': 'Post Buy Request',
        'button_text': 'Post Request',
        'is_edit': False
    }
    
    return render(request, 'iwanttobuy/request_form.html', context)


@login_required
def edit_request(request, pk):
    """View for editing an existing buy request"""
    
    buy_request = get_object_or_404(BuyRequest, pk=pk)
    
    # Check if user is the requester
    if buy_request.requester != request.user:
        return HttpResponseForbidden("You don't have permission to edit this request.")
    
    if request.method == 'POST':
        form = BuyRequestForm(request.POST, request.FILES, instance=buy_request)
        if form.is_valid():
            form.save()
            messages.success(request, "Your buy request has been updated successfully!")
            return redirect('iwanttobuy:request_detail', pk=buy_request.pk)
    else:
        form = BuyRequestForm(instance=buy_request)
    
    context = {
        'form': form,
        'buy_request': buy_request,
        'title': 'Edit Buy Request',
        'button_text': 'Update Request',
        'is_edit': True
    }
    
    return render(request, 'iwanttobuy/request_form.html', context)


@login_required
def delete_request(request, pk):
    """View for deleting/cancelling a buy request"""
    
    buy_request = get_object_or_404(BuyRequest, pk=pk)
    
    # Check if user is the requester
    if buy_request.requester != request.user:
        return HttpResponseForbidden("You don't have permission to delete this request.")
    
    if request.method == 'POST':
        # Just mark as cancelled, don't actually delete
        buy_request.status = 'CANCELLED'
        buy_request.save()
        messages.success(request, "Your buy request has been cancelled.")
        return redirect('iwanttobuy:my_requests')
    
    context = {
        'buy_request': buy_request,
        'title': 'Cancel Buy Request'
    }
    
    return render(request, 'iwanttobuy/request_confirm_delete.html', context)


@login_required
def mark_as_fulfilled(request, pk):
    """View to mark a buy request as fulfilled"""
    
    buy_request = get_object_or_404(BuyRequest, pk=pk)
    
    # Check if user is the requester
    if buy_request.requester != request.user:
        return HttpResponseForbidden("You don't have permission to update this request.")
    
    buy_request.status = 'FULFILLED'
    buy_request.save()
    
    messages.success(request, "Your buy request has been marked as fulfilled!")
    return redirect('iwanttobuy:request_detail', pk=buy_request.pk)


@login_required
def my_requests(request):
    """View to display a user's own buy requests"""
    
    buy_requests = BuyRequest.objects.filter(requester=request.user)
    
    # Filter by status
    status = request.GET.get('status', 'all')
    if status != 'all':
        buy_requests = buy_requests.filter(status=status.upper())
    
    buy_requests = buy_requests.order_by('-created_at')
    
    context = {
        'buy_requests': buy_requests,
        'status': status,
        'title': 'My Buy Requests'
    }
    
    return render(request, 'iwanttobuy/my_requests.html', context)


@login_required
def respond_to_request(request, pk):
    """View to respond to a buy request"""
    
    buy_request = get_object_or_404(BuyRequest, pk=pk)
    
    # Don't allow responding to your own request
    if buy_request.requester == request.user:
        messages.error(request, "You cannot respond to your own buy request.")
        return redirect('iwanttobuy:request_detail', pk=pk)
    
    # Don't allow responding to inactive requests
    if buy_request.status != 'ACTIVE':
        messages.error(request, "This buy request is no longer active.")
        return redirect('iwanttobuy:request_detail', pk=pk)
    
    if request.method == 'POST':
        form = BuyRequestResponseForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save(commit=False)
            response.buy_request = buy_request
            response.responder = request.user
            response.save()
            
            messages.success(request, "Your response has been sent to the requester!")
            return redirect('iwanttobuy:request_detail', pk=pk)
    else:
        form = BuyRequestResponseForm()
    
    context = {
        'form': form,
        'buy_request': buy_request,
        'title': f'Respond to {buy_request.title}'
    }
    
    return render(request, 'iwanttobuy/respond_form.html', context)


@login_required
def my_responses(request):
    """View to display responses sent by the user"""
    
    responses = BuyRequestResponse.objects.filter(responder=request.user)
    responses = responses.order_by('-created_at')
    
    context = {
        'responses': responses,
        'title': 'My Responses'
    }
    
    return render(request, 'iwanttobuy/my_responses.html', context)
