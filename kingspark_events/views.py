from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Event, EventRegistration
from .forms import EventForm, EventRegistrationForm

@login_required
def event_list(request):
    """List all approved upcoming events."""
    events = Event.objects.filter(
        status='approved',
        start_date__gte=timezone.now().date()
    ).order_by('start_date', 'start_time')

    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        events = events.filter(category=category)

    # Pagination
    paginator = Paginator(events, 12)  # Show 12 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': Event.CATEGORY_CHOICES,
        'selected_category': category,
    }
    return render(request, 'kingspark_events/event_list.html', context)

@login_required
def event_detail(request, event_id):
    """Display detailed information about a specific event."""
    event = get_object_or_404(Event, id=event_id, status='approved')
    user_registration = None
    registration_form = None

    # Check if user is already registered
    try:
        user_registration = EventRegistration.objects.get(event=event, attendee=request.user)
        registration_form = None  # Already registered
    except EventRegistration.DoesNotExist:
        if event.registration_required:
            registration_form = EventRegistrationForm()

    context = {
        'event': event,
        'user_registration': user_registration,
        'registration_form': registration_form,
        'is_organizer': event.organizer == request.user,
    }
    return render(request, 'kingspark_events/event_detail.html', context)

@login_required
def create_event(request):
    """Allow only admins to create new events."""
    # Check if user is admin
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only administrators can create events.")
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.status = 'approved'  # Auto-approve for admins
            event.approved_by = request.user
            event.approved_at = timezone.now()
            event.save()
            messages.success(
                request,
                'Your event has been created and published successfully.'
            )
            return redirect('kingspark_events:my_events')
    else:
        form = EventForm()

    return render(request, 'kingspark_events/create_event.html', {'form': form})

@login_required
def edit_event(request, event_id):
    """Allow only admins to edit events."""
    # Check if user is admin
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only administrators can edit events.")
    
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('kingspark_events:my_events')
    else:
        form = EventForm(instance=event)

    return render(request, 'kingspark_events/edit_event.html', {'form': form, 'event': event})

@login_required
def my_events(request):
    """Display events organized by the current user."""
    events = Event.objects.filter(organizer=request.user).order_by('-created_at')

    # Separate by status
    pending_events = events.filter(status='pending')
    approved_events = events.filter(status='approved')
    rejected_events = events.filter(status='rejected')

    context = {
        'pending_events': pending_events,
        'approved_events': approved_events,
        'rejected_events': rejected_events,
    }
    return render(request, 'kingspark_events/my_events.html', context)

@login_required
@require_POST
def register_for_event(request, event_id):
    """Handle event registration."""
    event = get_object_or_404(Event, id=event_id, status='approved')

    if not event.registration_required:
        messages.error(request, 'This event does not require registration.')
        return redirect('kingspark_events:event_detail', event_id=event.id)

    # Check if user is already registered
    if EventRegistration.objects.filter(event=event, attendee=request.user).exists():
        messages.error(request, 'You are already registered for this event.')
        return redirect('kingspark_events:event_detail', event_id=event.id)

    form = EventRegistrationForm(request.POST, event=event)
    if form.is_valid():
        registration = form.save(commit=False)
        registration.event = event
        registration.attendee = request.user
        registration.save()
        messages.success(request, f'Successfully registered for {event.title}!')
    else:
        messages.error(request, 'Registration failed. Please check your information.')

    return redirect('kingspark_events:event_detail', event_id=event.id)

@login_required
@require_POST
def unregister_from_event(request, event_id):
    """Handle event unregistration."""
    event = get_object_or_404(Event, id=event_id, status='approved')
    registration = get_object_or_404(EventRegistration, event=event, attendee=request.user)

    # Only allow cancellation if event hasn't started
    event_datetime = timezone.datetime.combine(event.start_date, event.start_time)
    event_datetime = timezone.make_aware(event_datetime)

    if event_datetime <= timezone.now():
        messages.error(request, 'You cannot unregister from an event that has already started.')
    else:
        registration.status = 'cancelled'
        registration.save()
        messages.success(request, f'Successfully unregistered from {event.title}.')

    return redirect('kingspark_events:event_detail', event_id=event.id)

@login_required
@require_POST
def delete_event(request, event_id):
    """Allow only admins to delete events."""
    # Check if user is admin
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Only administrators can delete events.")
    
    event = get_object_or_404(Event, id=event_id)

    event.delete()
    messages.success(request, 'Event deleted successfully.')
    return redirect('kingspark_events:my_events')