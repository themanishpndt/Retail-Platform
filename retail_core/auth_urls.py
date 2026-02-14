"""
URL Configuration for Advanced Authentication
Maps login, logout, and password change URLs
"""

from django.urls import path
from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from .auth_views import (
    CustomLoginView,
    CustomLogoutView,
    CustomPasswordChangeView,
    CustomPasswordChangeDoneView,
    SessionStatusView,
    SessionTimeoutWarningView,
)

app_name = 'auth'

urlpatterns = [
    # Authentication URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    
    # Password Change URLs
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    
    # Password Reset URLs
    path('password/reset/', PasswordResetView.as_view(
        template_name='admin/password_reset_form.html',
        email_template_name='admin/password_reset_email.html',
        success_url='/admin/password/reset/done/',
    ), name='password_reset'),
    
    path('password/reset/done/', PasswordResetDoneView.as_view(
        template_name='admin/password_reset_done.html',
    ), name='password_reset_done'),
    
    path('password/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='admin/password_reset_confirm.html',
        success_url='/admin/password/reset/complete/',
    ), name='password_reset_confirm'),
    
    path('password/reset/complete/', PasswordResetCompleteView.as_view(
        template_name='admin/password_reset_complete.html',
    ), name='password_reset_complete'),
    
    # Session URLs
    path('session/status/', SessionStatusView.as_view(), name='session_status'),
    path('session/timeout-warning/', SessionTimeoutWarningView.as_view(), name='session_timeout_warning'),
]
