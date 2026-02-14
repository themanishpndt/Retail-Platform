"""
User Authentication Views for Retail Platform
Handles user registration, login, logout, and password management
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, CreateView
from django.contrib import messages
from django.contrib.auth.models import User
from django import forms
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


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

class CustomUserCreationForm(UserCreationForm):
    """Enhanced user registration form with additional validation"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a strong password'
        })
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'This email address is already registered.',
                code='email_exists'
            )
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise forms.ValidationError(
                'Username must be at least 3 characters long.',
                code='username_too_short'
            )
        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password and len(password) < 8:
            raise forms.ValidationError(
                'Password must be at least 8 characters long.',
                code='password_too_short'
            )
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Enhanced login form for users"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Allow login with email or username
            try:
                user = User.objects.get(email=username)
                username = user.username
            except User.DoesNotExist:
                pass

            if not User.objects.filter(username=username, is_active=True).exists():
                raise forms.ValidationError(
                    'Invalid username/email or password.',
                    code='invalid_credentials'
                )

        return super().clean()


# ============================================================
# USER AUTHENTICATION VIEWS
# ============================================================

class UserSignupView(CreateView):
    """Handle user registration"""
    form_class = CustomUserCreationForm
    template_name = 'user_auth/signup.html'
    success_url = reverse_lazy('user:dashboard')

    def form_valid(self, form):
        user = form.save()
        
        # Log the registration
        logger.info(
            f"New user registered: {user.username} - "
            f"Email: {user.email} - IP: {get_client_ip(self.request)}"
        )
        
        # Auto-login the user
        login(self.request, user)
        messages.success(
            self.request,
            f'Welcome {user.first_name}! Your account has been created successfully.'
        )
        
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            f"User registration failed - IP: {get_client_ip(self.request)} - "
            f"Errors: {form.errors}"
        )
        return super().form_invalid(form)


class UserLoginView(LoginView):
    """Handle user login"""
    form_class = CustomAuthenticationForm
    template_name = 'user_auth/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('user:dashboard')

    def form_valid(self, form):
        user = form.get_user()
        
        # Log successful login
        logger.info(
            f"User login: {user.username} - IP: {get_client_ip(self.request)}"
        )
        
        # Set session
        login(self.request, user)
        
        # Handle remember me
        remember = self.request.POST.get('remember_me')
        if remember:
            self.request.session.set_expiry(7 * 24 * 60 * 60)  # 7 days
        
        messages.success(self.request, f'Welcome back, {user.first_name}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            f"User login failed - IP: {get_client_ip(self.request)} - "
            f"Username: {self.request.POST.get('username', 'unknown')}"
        )
        messages.error(
            self.request,
            'Invalid username/email or password. Please try again.'
        )
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    """Handle user logout"""
    template_name = 'user_auth/logged_out.html'
    next_page = 'user:login'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logger.info(
                f"User logout: {request.user.username} - IP: {get_client_ip(request)}"
            )
            messages.success(request, 'You have been logged out successfully.')
        
        return super().dispatch(request, *args, **kwargs)


class UserPasswordChangeView(PasswordChangeView):
    """Handle user password change"""
    template_name = 'user_auth/password_change_form.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('user:password_change_done')

    def form_valid(self, form):
        logger.info(
            f"User password changed: {self.request.user.username} - "
            f"IP: {get_client_ip(self.request)}"
        )
        messages.success(
            self.request,
            'Your password has been changed successfully.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(
            f"Password change failed for {self.request.user.username} - "
            f"Errors: {form.errors}"
        )
        return super().form_invalid(form)


class UserPasswordChangeDoneView(PasswordChangeDoneView):
    """Password change success page"""
    template_name = 'user_auth/password_change_done.html'


class UserPasswordResetView(PasswordResetView):
    """Handle password reset request"""
    template_name = 'user_auth/password_reset_form.html'
    email_template_name = 'user_auth/password_reset_email.txt'
    subject_template_name = 'user_auth/password_reset_subject.txt'
    success_url = reverse_lazy('user:password_reset_done')
    
    def form_valid(self, form):
        logger.info(
            f"Password reset requested - Email: {form.cleaned_data.get('email')} - "
            f"IP: {get_client_ip(self.request)}"
        )
        messages.info(
            self.request,
            'Check your email for a link to reset your password.'
        )
        return super().form_valid(form)


class UserPasswordResetDoneView(PasswordResetDoneView):
    """Password reset email sent confirmation"""
    template_name = 'user_auth/password_reset_done.html'


# ============================================================
# DASHBOARD & PROFILE VIEWS
# ============================================================

class UserDashboardView(View):
    """User dashboard view"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('user:login')
        
        context = {
            'user': request.user,
            'registered_date': request.user.date_joined,
            'last_login': request.user.last_login,
        }
        
        return render(request, 'dashboard.html', context)


class UserProfileView(View):
    """User profile view"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('user:login')

        profile = getattr(request.user, 'profile', None)
        context = {
            'user': request.user,
            'profile': profile,
        }
        return render(request, 'user_auth/profile.html', context)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('user:login')

        user = request.user
        profile = getattr(user, 'profile', None)

        # Handle avatar upload
        if 'avatar' in request.FILES and profile:
            profile.avatar = request.FILES['avatar']
            profile.save()
            messages.success(request, 'Profile picture updated!')
            logger.info(f"User avatar updated: {user.username} - IP: {get_client_ip(request)}")
            return redirect('user:profile')

        # Handle profile info update
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        logger.info(
            f"User profile updated: {user.username} - IP: {get_client_ip(request)}"
        )

        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('user:profile')


# ============================================================
# HOME PAGE VIEW
# ============================================================

class HomeView(View):
    """Home page - shows public homepage or redirects authenticated users"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('user:dashboard')
        else:
            return render(request, 'user_auth/home.html')
