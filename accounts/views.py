from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth.tokens import default_token_generator

from .forms import UserRegistrationForm, CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm
from .models import Profile
from .decorators import account_not_locked

import logging
import uuid
from datetime import timedelta

# Set up logger
logger = logging.getLogger(__name__)

def register(request):
    """Enhanced registration view with email verification."""
    if request.user.is_authenticated:
        messages.info(request, 'You are already registered and logged in.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create inactive user account
            user = form.save(commit=False)
            user.is_active = False  # Account inactive until email verified
            user.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Generate verification code
            verification_code = user.profile.create_verification_code()
            
            # Send verification email
            current_site = get_current_site(request)
            mail_subject = 'Activate your Kings Park CPF account'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            
            # Log the attempt to send email
            try:
                send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                logger.info(f'Verification email sent to {user.email}')
                messages.success(request, 'Registration successful! Please check your email to activate your account.')
                return redirect('account_activation_sent')
            except Exception as e:
                logger.error(f'Failed to send verification email: {str(e)}')
                messages.error(request, 'There was an error sending the verification email. Please try again.')
                user.delete()  # Clean up on failure
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {
        'form': form,
        'title': 'Register',
        'button_text': 'Sign Up',
    })


def account_activation_sent(request):
    """View shown after registration when activation email is sent."""
    return render(request, 'account_activation_sent.html')


def activate_account(request, uidb64, token):
    """Activate user account using email verification."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.profile.is_verified = True
        user.profile.verification_status = 'VERIFIED'
        user.save()
        user.profile.save()
        login(request, user)
        messages.success(request, 'Your account has been activated successfully!')
        return redirect('home')
    else:
        messages.error(request, 'The activation link is invalid or has expired.')
        return redirect('invalid_activation')


def invalid_activation(request):
    """View shown when activation link is invalid."""
    return render(request, 'invalid_activation.html')


@account_not_locked
def login_view(request):
    """Enhanced login view with security features."""
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Your account is not active. Please check your email for activation instructions.')
                    return redirect('account_activation_sent')
                
                # Security check for approved users
                if hasattr(user, 'profile') and not user.profile.is_approved and user.profile.role in ['POLICE_OFFICER', 'ADMIN', 'CPF_MEMBER']:
                    messages.warning(request, 'Your account requires approval for the selected role. Please contact the administrator.')
                    return redirect('login')
                
                # Record successful login
                ip_address = get_client_ip(request)
                user.profile.record_login_attempt(successful=True, ip_address=ip_address)
                
                # Log the user in
                login(request, user)
                logger.info(f'User {username} logged in successfully from IP: {ip_address}')
                
                # Redirect to intended page or home
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('home')
            else:
                # Record failed login attempt if user exists
                try:
                    user = User.objects.get(username=username)
                    ip_address = get_client_ip(request)
                    user.profile.record_login_attempt(successful=False, ip_address=ip_address)
                    logger.warning(f'Failed login attempt for user {username} from IP: {ip_address}')
                    
                    # Check if account is now locked
                    if user.profile.is_locked():
                        locked_until = user.profile.account_locked_until
                        minutes = round((locked_until - timezone.now()).total_seconds() / 60)
                        messages.error(request, f'Your account has been temporarily locked due to multiple failed login attempts. Please try again in {minutes} minutes.')
                except User.DoesNotExist:
                    logger.warning(f'Login attempt with non-existent username: {username}')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {
        'form': form,
        'title': 'Login',
        'button_text': 'Sign In',
    })


def logout_view(request):
    """Log out the user and redirect to home page."""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    """User profile view and edit functionality."""
    if request.method == 'POST':
        # Process profile update
        # This would be expanded with a proper form for profile editing
        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('profile')
    
    return render(request, 'profile.html')


@login_required
def change_password(request):
    """Change password view."""
    if request.method == 'POST':
        form = CustomSetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
    else:
        form = CustomSetPasswordForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
