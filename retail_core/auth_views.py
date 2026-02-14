"""
Advanced Authentication Views for Django Admin
Handles login, logout, and password change with proper flow and logging
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.contrib import messages
from django import forms
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib.auth.models import User
import logging
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)


# ============================================================
# DECORATORS & MIDDLEWARE
# ============================================================

def log_activity(action_type):
    """Decorator to log user activities"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                logger.info(
                    f"User {request.user.username} - {action_type} - "
                    f"IP: {get_client_ip(request)} - Time: {datetime.now()}"
                )
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ============================================================
# CUSTOM FORMS
# ============================================================

class CustomAuthenticationForm(AuthenticationForm):
    """Enhanced authentication form with additional validation"""
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            try:
                user = User.objects.get(username=username)
                
                # Check if user account is active
                if not user.is_active:
                    raise forms.ValidationError(
                        "This account has been disabled. Please contact an administrator.",
                        code='inactive_account'
                    )
                
                # Check if user is a superuser/staff
                if not user.is_staff:
                    raise forms.ValidationError(
                        "You don't have permission to access the admin panel.",
                        code='insufficient_permissions'
                    )
                    
            except User.DoesNotExist:
                pass

        return super().clean()


class CustomPasswordChangeForm(PasswordChangeForm):
    """Enhanced password change form with validation"""
    
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        
        if password and len(password) < 8:
            raise forms.ValidationError(
                "Password must be at least 8 characters long.",
                code='password_too_short'
            )
        
        # Check for common patterns
        if password and password.isdigit():
            raise forms.ValidationError(
                "Password cannot be entirely numeric.",
                code='numeric_password'
            )
        
        return password


# ============================================================
# AUTHENTICATION VIEWS
# ============================================================

class CustomLoginView(LoginView):
    """
    Enhanced login view with logging, session management, and security features
    """
    template_name = 'admin/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to admin dashboard after successful login"""
        return reverse_lazy('admin:index')
    
    def form_valid(self, form):
        """Handle successful login"""
        user = form.get_user()
        
        # Log the login attempt
        logger.info(
            f"✓ User Login: {user.username} | "
            f"IP: {get_client_ip(self.request)} | "
            f"Timestamp: {datetime.now()}"
        )
        
        # Login the user
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Set session timeout (optional)
        if not self.request.POST.get('remember'):
            # Session expires when browser closes if not remembered
            self.request.session.set_expiry(0)
        else:
            # Remember for 7 days
            self.request.session.set_expiry(7 * 24 * 60 * 60)
        
        # Add success message
        messages.success(self.request, f"Welcome back, {user.get_full_name() or user.username}!")
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle failed login"""
        username = form.cleaned_data.get('username', 'Unknown')
        logger.warning(
            f"✗ Failed Login Attempt: {username} | "
            f"IP: {get_client_ip(self.request)} | "
            f"Timestamp: {datetime.now()}"
        )
        
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add additional context to login page"""
        context = super().get_context_data(**kwargs)
        context['site_title'] = 'Retail Platform Admin'
        context['site_header'] = 'Admin Login'
        return context


class CustomLogoutView(LogoutView):
    """
    Enhanced logout view with logging and session cleanup
    """
    template_name = 'admin/logged_out.html'
    next_page = None
    
    def dispatch(self, request, *args, **kwargs):
        """Log logout activity before session is destroyed"""
        if request.user.is_authenticated:
            logger.info(
                f"✓ User Logout: {request.user.username} | "
                f"IP: {get_client_ip(request)} | "
                f"Session Duration: {self._get_session_duration(request)} | "
                f"Timestamp: {datetime.now()}"
            )
        
        return super().dispatch(request, *args, **kwargs)
    
    def _get_session_duration(self, request):
        """Calculate session duration"""
        try:
            login_time = request.session.get('login_time')
            if login_time:
                duration = datetime.now() - login_time
                return str(duration)
        except:
            pass
        return "Unknown"
    
    def get_next_page(self):
        """Redirect to login page after logout"""
        if self.next_page is None:
            return reverse_lazy('admin:login')
        return self.next_page
    
    def get_context_data(self, **kwargs):
        """Add context data to logged out page"""
        context = {}
        context['last_login'] = self.request.user.last_login
        return context


class CustomPasswordChangeView(PasswordChangeView):
    """
    Enhanced password change view with validation and logging
    """
    template_name = 'admin/password_change_form.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('admin:password_change_done')
    
    @method_decorator(csrf_protect)
    @method_decorator(log_activity('PASSWORD_CHANGE_ATTEMPT'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Handle successful password change"""
        user = form.save()
        
        # Log the password change
        logger.info(
            f"✓ Password Changed: {user.username} | "
            f"IP: {get_client_ip(self.request)} | "
            f"Timestamp: {datetime.now()}"
        )
        
        # Keep the user logged in after password change
        login(
            self.request,
            user,
            backend='django.contrib.auth.backends.ModelBackend'
        )
        
        messages.success(self.request, "Your password has been changed successfully!")
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle failed password change"""
        logger.warning(
            f"✗ Failed Password Change: {self.request.user.username} | "
            f"IP: {get_client_ip(self.request)} | "
            f"Errors: {form.errors} | "
            f"Timestamp: {datetime.now()}"
        )
        
        messages.error(self.request, "Failed to change password. Please check your input.")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add context data"""
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Change Your Password'
        return context


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    """
    Enhanced password change done view
    """
    template_name = 'admin/password_change_done.html'
    
    def get_context_data(self, **kwargs):
        """Add context data"""
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['password_change_date'] = datetime.now()
        return context


# ============================================================
# SESSION MANAGEMENT VIEWS
# ============================================================

class SessionStatusView(View):
    """Check session status and user info"""
    
    def get(self, request):
        """Get current session information"""
        if not request.user.is_authenticated:
            return redirect('admin:login')
        
        context = {
            'user': request.user,
            'username': request.user.username,
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
            'last_login': request.user.last_login,
            'date_joined': request.user.date_joined,
            'session_key': request.session.session_key,
        }
        
        return render(request, 'admin/session_status.html', context)


class SessionTimeoutWarningView(View):
    """Show session timeout warning"""
    
    def get(self, request):
        """Display session timeout warning"""
        return render(request, 'admin/session_timeout.html')


# ============================================================
# SECURITY VIEWS
# ============================================================

class LoginAttemptsView(View):
    """Track and limit login attempts"""
    
    def get_failed_attempts(self, request):
        """Get number of failed login attempts"""
        cache_key = f"login_attempts_{get_client_ip(request)}"
        from django.core.cache import cache
        return cache.get(cache_key, 0)
    
    def increment_failed_attempts(self, request):
        """Increment failed login attempts"""
        cache_key = f"login_attempts_{get_client_ip(request)}"
        from django.core.cache import cache
        attempts = cache.get(cache_key, 0) + 1
        cache.set(cache_key, attempts, 60 * 15)  # 15 minutes
        return attempts
    
    def reset_failed_attempts(self, request):
        """Reset failed login attempts"""
        cache_key = f"login_attempts_{get_client_ip(request)}"
        from django.core.cache import cache
        cache.delete(cache_key)


# ============================================================
# AUDIT LOGGING
# ============================================================

class AuditLogger:
    """Log all authentication activities"""
    
    @staticmethod
    def log_login(user, ip, success=True):
        """Log login attempt"""
        action = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
        logger.info(
            f"{action} | User: {user.username if user else 'Unknown'} | "
            f"IP: {ip} | Timestamp: {datetime.now()}"
        )
    
    @staticmethod
    def log_logout(user, ip, session_duration=None):
        """Log logout"""
        logger.info(
            f"LOGOUT | User: {user.username} | "
            f"IP: {ip} | Duration: {session_duration} | "
            f"Timestamp: {datetime.now()}"
        )
    
    @staticmethod
    def log_password_change(user, ip, success=True):
        """Log password change"""
        action = "PASSWORD_CHANGE_SUCCESS" if success else "PASSWORD_CHANGE_FAILED"
        logger.info(
            f"{action} | User: {user.username} | "
            f"IP: {ip} | Timestamp: {datetime.now()}"
        )


# ============================================================
# CONTEXT PROCESSORS
# ============================================================

def auth_context(request):
    """Add authentication context to all templates"""
    return {
        'is_authenticated': request.user.is_authenticated,
        'current_user': request.user if request.user.is_authenticated else None,
        'user_full_name': request.user.get_full_name() if request.user.is_authenticated else None,
        'user_email': request.user.email if request.user.is_authenticated else None,
    }
