from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def account_not_locked(view_func):
    """
    Decorator to check if a user's account is locked.
    If locked, redirects to login page with an appropriate message.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Skip check for non-POST requests
        if request.method != 'POST':
            return view_func(request, *args, **kwargs)

        # Check if username exists in POST data
        username = request.POST.get('username')
        if not username:
            return view_func(request, *args, **kwargs)
        
        # Import User model here to avoid circular imports
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username=username)
            
            # Check if account is locked
            if hasattr(user, 'profile') and user.profile.is_locked():
                locked_until = user.profile.account_locked_until
                minutes = round((locked_until - timezone.now()).total_seconds() / 60)
                messages.error(request, f'Your account has been temporarily locked due to multiple failed login attempts. Please try again in {minutes} minutes.')
                logger.warning(f'Locked account access attempt: {username}')
                return redirect('login')
        except User.DoesNotExist:
            # Username doesn't exist, continue to view for proper error handling
            pass
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def role_required(roles):
    """
    Decorator to restrict access based on user role.
    Accepts a list of allowed roles.
    """
    def check_role(user):
        # Check if user is authenticated and has required role
        if not user.is_authenticated:
            return False
            
        if not hasattr(user, 'profile'):
            return False
            
        return user.profile.role in roles
    
    # Return the decorator with the check function
    return user_passes_test(
        check_role, 
        login_url='login',
        redirect_field_name='next'
    )


def verified_account_required(function):
    """
    Decorator to ensure account is verified before accessing a view.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if request.user.profile.is_verified:
                return function(request, *args, **kwargs)
            else:
                messages.warning(request, 'You need to verify your account before accessing this page.')
                return redirect('account_activation_sent')
        return redirect('login')
    return wrap


def approved_account_required(function):
    """
    Decorator to ensure account is approved before accessing a view.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if request.user.profile.is_approved or request.user.profile.role not in ['POLICE_OFFICER', 'ADMIN', 'CPF_MEMBER']:
                return function(request, *args, **kwargs)
            else:
                messages.warning(request, 'Your account requires approval before you can access this feature.')
                return redirect('home')
        return redirect('login')
    return wrap
