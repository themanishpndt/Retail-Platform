"""
URL Configuration for User Authentication
Maps user login, signup, and password management URLs
"""

from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from .user_views import (
    HomeView,
    UserSignupView,
    UserLoginView,
    UserLogoutView,
    UserPasswordChangeView,
    UserPasswordChangeDoneView,
    UserPasswordResetView,
    UserPasswordResetDoneView,
    UserDashboardView,
    UserProfileView,
)

app_name = 'user'

urlpatterns = [
    # Home page redirect
    path('', HomeView.as_view(), name='home'),
    
    # Authentication URLs - Root level (for main homepage)
    path('login/', UserLoginView.as_view(), name='login'),
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # Account Dashboard & Profile URLs
    path('account/dashboard/', UserDashboardView.as_view(), name='dashboard'),
    path('account/profile/', UserProfileView.as_view(), name='profile'),
    
    # Password Management URLs
    path('account/password/change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('account/password/change/done/', UserPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('account/password/reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('account/password/reset/done/', UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('account/password/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='user_auth/password_reset_confirm.html',
        success_url=reverse_lazy('user:password_reset_complete'),
    ), name='password_reset_confirm'),
    path('account/password/reset/complete/', PasswordResetCompleteView.as_view(
        template_name='user_auth/password_reset_complete.html'
    ), name='password_reset_complete'),
]
