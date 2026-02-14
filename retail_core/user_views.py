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
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

# Import models for dashboard
from orders.models import Order, OrderLine
from products.models import Product
from inventory.models import InventoryLevel, Store
from analytics.models import DailySalesMetrics, ProductSalesAnalytics
from alerts.models import Alert
from ml_services.models import ForecastModel

# Import OTP model
from retail_core.models import PasswordResetOTP

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
    """User dashboard view with analytics and business metrics"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('user:login')
        
        # Calculate 30-day range
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Get all orders from last 30 days
        orders_30days = Order.objects.filter(
            order_date__gte=timezone.make_aware(datetime.combine(thirty_days_ago, datetime.min.time()))
        )
        
        # 1. Revenue (30 Days)
        total_revenue = orders_30days.aggregate(Sum('total'))['total__sum'] or 0
        
        # 2. Total Orders
        total_orders = orders_30days.count()
        
        # 3. Average Order Value
        avg_order_value = orders_30days.aggregate(Avg('total'))['total__avg'] or 0
        
        # 4. Low Stock Items (quantity < 10)
        low_stock_items = InventoryLevel.objects.filter(
            quantity_on_hand__lt=10
        ).select_related('product', 'store').count()
        
        # 5. Top 5 Products (by quantity sold in last 30 days)
        top_products = OrderLine.objects.filter(
            order__order_date__gte=timezone.make_aware(datetime.combine(thirty_days_ago, datetime.min.time()))
        ).values('product__name', 'product__sku').annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('line_total')
        ).order_by('-total_sold')[:5]
        
        # 6. Sales Trend (Daily sales for last 30 days)
        sales_trend = []
        for i in range(30):
            date = today - timedelta(days=i)
            daily_orders = Order.objects.filter(
                order_date__date=date
            )
            daily_revenue = daily_orders.aggregate(Sum('total'))['total__sum'] or 0
            sales_trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'revenue': float(daily_revenue),
                'orders': daily_orders.count()
            })
        sales_trend.reverse()  # Reverse to start from oldest
        
        # 7. Inventory Status by Store (total items per store)
        inventory_by_store = InventoryLevel.objects.values('store__name').annotate(
            total_quantity=Sum('quantity_on_hand'),
            store_id=Sum('store__id')
        )
        
        # 8. Active Alerts (excluding resolved/closed)
        active_alerts = Alert.objects.filter(
            status__in=['ACTIVE', 'ACKNOWLEDGED']
        ).select_related('store', 'inventory_level__product').order_by('-triggered_at')[:10]
        
        # 9. Forecast data (next 7 days)
        forecast_data = []
        for i in range(7):
            date = today + timedelta(days=i)
            forecast_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'forecasted_demand': 100 + (i * 15)  # Placeholder data
            })
        
        context = {
            'user': request.user,
            'registered_date': request.user.date_joined,
            'last_login': request.user.last_login,
            # KPI Metrics
            'total_revenue': f"${total_revenue:,.2f}",
            'total_revenue_raw': float(total_revenue),
            'total_orders': total_orders,
            'low_stock_items': low_stock_items,
            'avg_order_value': f"${avg_order_value:,.2f}",
            'avg_order_value_raw': float(avg_order_value),
            # Charts and detailed data
            'top_products': list(top_products),
            'sales_trend': sales_trend,
            'inventory_by_store': list(inventory_by_store),
            'forecast_data': forecast_data,
            'active_alerts': active_alerts,
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


# ============================================================
# PASSWORD RESET WITH OTP
# ============================================================

class PasswordResetRequestView(View):
    """Request password reset - send OTP to email"""
    
    def get(self, request):
        return render(request, 'user_auth/password_reset_request.html')
    
    def post(self, request):
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'user_auth/password_reset_request.html')
        
        try:
            # Check if user exists
            user = User.objects.get(email=email)
            
            # Generate and save OTP
            otp_obj = PasswordResetOTP.create_otp(email=email, user=user)
            
            # Send OTP via email
            subject = 'Password Reset OTP - Retail Platform'
            message = f"""
Hello {user.first_name or 'User'},

Your password reset OTP is: {otp_obj.otp}

This OTP will expire in 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
Retail Platform Team
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'OTP sent to your email. Please check your inbox.')
                return redirect('user:password_reset_verify', email=email)
            except Exception as e:
                logger.error(f"Failed to send OTP email: {str(e)}")
                messages.error(request, 'Failed to send OTP. Please try again later.')
                return render(request, 'user_auth/password_reset_request.html')
                
        except User.DoesNotExist:
            # For security, don't reveal if email exists
            messages.info(request, 'If an account exists with this email, an OTP has been sent.')
            return render(request, 'user_auth/password_reset_request.html')
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            messages.error(request, 'An error occurred. Please try again.')
            return render(request, 'user_auth/password_reset_request.html')


class PasswordResetVerifyOTPView(View):
    """Verify OTP for password reset"""
    
    def get(self, request, email=None):
        email = email or request.GET.get('email', '')
        context = {'email': email}
        return render(request, 'user_auth/password_reset_verify_otp.html', context)
    
    def post(self, request):
        email = request.POST.get('email', '').strip()
        otp_code = request.POST.get('otp', '').strip()
        
        if not email or not otp_code:
            messages.error(request, 'Email and OTP are required.')
            return render(request, 'user_auth/password_reset_verify_otp.html', {'email': email})
        
        # Verify OTP
        otp_obj = PasswordResetOTP.verify_otp(email, otp_code)
        
        if otp_obj:
            # Mark OTP as used
            otp_obj.is_used = True
            otp_obj.save()
            
            # Redirect to password reset form
            messages.success(request, 'OTP verified successfully. Please set your new password.')
            return redirect('user:password_reset_set_new', email=email, otp=otp_code)
        else:
            # Increment attempts
            try:
                failed_otp = PasswordResetOTP.objects.filter(
                    email=email,
                    is_used=False,
                    expires_at__gt=timezone.now()
                ).first()
                
                if failed_otp:
                    failed_otp.attempts += 1
                    failed_otp.save()
                    
                    if failed_otp.attempts >= 3:
                        messages.error(request, 'Too many failed attempts. Please request a new OTP.')
                        return redirect('user:password_reset_request')
            except:
                pass
            
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, 'user_auth/password_reset_verify_otp.html', {'email': email})


class PasswordResetSetNewView(View):
    """Set new password after OTP verification"""
    
    def get(self, request, email=None, otp=None):
        email = email or request.GET.get('email', '')
        otp = otp or request.GET.get('otp', '')
        
        # Verify OTP is still valid
        if not PasswordResetOTP.objects.filter(email=email, otp=otp, is_used=True).exists():
            messages.error(request, 'Invalid or expired OTP.')
            return redirect('user:password_reset_request')
        
        context = {'email': email, 'otp': otp}
        return render(request, 'user_auth/password_reset_set_new.html', context)
    
    def post(self, request):
        email = request.POST.get('email', '').strip()
        otp = request.POST.get('otp', '').strip()
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not email or not otp:
            messages.error(request, 'Invalid request.')
            return redirect('user:password_reset_request')
        
        # Verify passwords match
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            context = {'email': email, 'otp': otp}
            return render(request, 'user_auth/password_reset_set_new.html', context)
        
        # Verify password strength
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            context = {'email': email, 'otp': otp}
            return render(request, 'user_auth/password_reset_set_new.html', context)
        
        # Verify OTP was used
        if not PasswordResetOTP.objects.filter(email=email, otp=otp, is_used=True).exists():
            messages.error(request, 'Invalid or expired OTP.')
            return redirect('user:password_reset_request')
        
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            messages.success(request, 'Your password has been reset successfully. Please log in.')
            return redirect('user:login')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('user:password_reset_request')
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            messages.error(request, 'An error occurred. Please try again.')
            context = {'email': email, 'otp': otp}
            return render(request, 'user_auth/password_reset_set_new.html', context)
