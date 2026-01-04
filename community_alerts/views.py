from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Alert, AlertCategory, AlertReceipt
from .forms import AlertForm
from reports.tasks import send_sms_alert  # Reuse the existing SMS function

def is_staff_or_admin(user):
    """Check if user is staff, admin, or has special roles"""
    return user.is_authenticated and (
        user.is_staff or 
        user.is_superuser or 
        (hasattr(user, 'profile') and user.profile.role in ['POLICE_OFFICER', 'ADMIN', 'CPF_MEMBER'])
    )

@login_required
def alert_list(request):
    """View for listing all active alerts"""
    # Get all active alerts
    alerts = Alert.objects.filter(
        Q(is_approved=True),
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).order_by('-created_at')
    
    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        alerts = alerts.filter(category__id=category)
    
    # Filter by severity if provided
    severity = request.GET.get('severity')
    if severity:
        alerts = alerts.filter(severity=severity)
    
    # Get all categories for filter dropdown
    categories = AlertCategory.objects.all()
    
    # Mark alerts as viewed for the current user
    if request.user.is_authenticated:
        for alert in alerts:
            receipt, created = AlertReceipt.objects.get_or_create(
                alert=alert,
                user=request.user
            )
            if not receipt.viewed:
                receipt.viewed = True
                receipt.viewed_at = timezone.now()
                receipt.save()
    
    # Pagination
    paginator = Paginator(alerts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category,
        'selected_severity': severity,
        'severity_choices': Alert.SEVERITY_CHOICES,
    }
    
    return render(request, 'community_alerts/alert_list.html', context)

@login_required
def alert_detail(request, pk):
    """View for showing a single alert"""
    alert = get_object_or_404(Alert, pk=pk)
    
    # Mark alert as viewed
    if request.user.is_authenticated:
        receipt, created = AlertReceipt.objects.get_or_create(
            alert=alert,
            user=request.user
        )
        if not receipt.viewed:
            receipt.viewed = True
            receipt.viewed_at = timezone.now()
            receipt.save()
    
    context = {
        'alert': alert,
        'can_manage': is_staff_or_admin(request.user),
    }
    
    return render(request, 'community_alerts/alert_detail.html', context)

@login_required
@user_passes_test(is_staff_or_admin, login_url='/accounts/login/')
def create_alert(request):
    """View for creating a new alert"""
    if request.method == 'POST':
        form = AlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.created_by = request.user
            
            # Auto-approve for admins
            if request.user.is_superuser or request.user.profile.role == 'ADMIN':
                alert.is_approved = True
                alert.approved_by = request.user
            
            alert.save()
            
            messages.success(request, 'Alert created successfully!')
            
            # If approved and should be sent immediately
            if alert.is_approved and request.POST.get('send_now') == 'yes':
                return redirect('community_alerts:send_alert', pk=alert.pk)
            
            return redirect('community_alerts:alert_list')
    else:
        form = AlertForm()
    
    context = {
        'form': form,
        'title': 'Create Community Alert',
        'button_text': 'Create Alert',
    }
    
    return render(request, 'community_alerts/alert_form.html', context)

@login_required
@user_passes_test(is_staff_or_admin, login_url='/accounts/login/')
def edit_alert(request, pk):
    """View for editing an existing alert"""
    alert = get_object_or_404(Alert, pk=pk)
    
    if request.method == 'POST':
        form = AlertForm(request.POST, instance=alert)
        if form.is_valid():
            alert = form.save()
            messages.success(request, 'Alert updated successfully!')
            return redirect('community_alerts:alert_detail', pk=alert.pk)
    else:
        form = AlertForm(instance=alert)
    
    context = {
        'form': form,
        'alert': alert,
        'title': 'Edit Community Alert',
        'button_text': 'Update Alert',
    }
    
    return render(request, 'community_alerts/alert_form.html', context)

@login_required
@user_passes_test(is_staff_or_admin, login_url='/accounts/login/')
def approve_alert(request, pk):
    """View for approving an alert"""
    alert = get_object_or_404(Alert, pk=pk)
    
    if not alert.is_approved:
        alert.is_approved = True
        alert.approved_by = request.user
        alert.save()
        messages.success(request, 'Alert approved successfully!')
    
    return redirect('community_alerts:alert_detail', pk=alert.pk)

@login_required
@user_passes_test(is_staff_or_admin, login_url='/accounts/login/')
def send_alert(request, pk):
    """View for sending an alert"""
    alert = get_object_or_404(Alert, pk=pk)
    
    if not alert.is_approved:
        messages.error(request, 'Alert must be approved before sending!')
        return redirect('community_alerts:alert_detail', pk=alert.pk)
    
    if request.method == 'POST':
        # Get list of users to send to
        from django.contrib.auth.models import User
        
        # Only send to users who have opted in for notifications
        users_to_notify = User.objects.filter(
            profile__email_notifications=True if alert.send_email else False,
            profile__sms_notifications=True if alert.send_sms else False,
        )
        
        # Record receipts and send notifications
        for user in users_to_notify:
            # Create receipt
            receipt, created = AlertReceipt.objects.get_or_create(
                alert=alert,
                user=user
            )
            
            # Send email if enabled
            if alert.send_email and not receipt.sent_via_email:
                try:
                    from django.core.mail import send_mail
                    send_mail(
                        f"ALERT: {alert.title}",
                        f"{alert.content}\n\nThis alert was sent on {timezone.now().strftime('%d %B %Y at %H:%M')}.",
                        from_email=None,  # Use DEFAULT_FROM_EMAIL from settings
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    receipt.sent_via_email = True
                    receipt.save()
                except Exception as e:
                    messages.error(request, f"Error sending email: {e}")
            
            # Send SMS if enabled and user has phone number
            if alert.send_sms and hasattr(user, 'profile') and user.profile.phone_number and not receipt.sent_via_sms:
                try:
                    message = f"ALERT: {alert.title} - {alert.content[:100]}"
                    send_sms_alert.delay(user.profile.phone_number, message)
                    receipt.sent_via_sms = True
                    receipt.save()
                except Exception as e:
                    messages.error(request, f"Error sending SMS: {e}")
        
        # Update alert
        alert.is_sent = True
        alert.sent_at = timezone.now()
        alert.save()
        
        messages.success(request, f"Alert sent to {users_to_notify.count()} users.")
        return redirect('community_alerts:alert_detail', pk=alert.pk)
    
    # Confirmation page
    return render(request, 'community_alerts/send_alert_confirm.html', {'alert': alert})

@login_required
def unread_alerts_count(request):
    """API endpoint to get the number of unread alerts for the current user"""
    if not request.user.is_authenticated:
        return JsonResponse({'count': 0})
    
    # Get active alerts
    active_alerts = Alert.objects.filter(
        Q(is_approved=True),
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    )
    
    # Get alerts user hasn't viewed
    unread_count = active_alerts.exclude(
        receipts__user=request.user,
        receipts__viewed=True
    ).count()
    
    return JsonResponse({'count': unread_count})
