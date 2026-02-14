"""
SMTP Configuration API Views
Handles testing and saving SMTP email settings
"""

import json
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import smtplib
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class TestSMTPView(View):
    """Test SMTP connection with provided credentials"""
    
    def post(self, request):
        try:
            email_backend = request.POST.get('email_backend', settings.EMAIL_BACKEND)
            email_host = request.POST.get('email_host', settings.EMAIL_HOST)
            email_port = int(request.POST.get('email_port', settings.EMAIL_PORT))
            email_use_tls = request.POST.get('email_use_tls') == 'on'
            email_host_user = request.POST.get('email_host_user', '')
            email_host_password = request.POST.get('email_host_password', '')
            
            # Skip test if using console backend
            if 'console' in email_backend:
                return JsonResponse({
                    'success': True,
                    'message': 'Console backend selected. Emails will be displayed in terminal (development only).'
                })
            
            # Test SMTP connection
            if not email_host_user or not email_host_password:
                return JsonResponse({
                    'success': False,
                    'message': 'Email address and app password are required.'
                })
            
            try:
                server = smtplib.SMTP(email_host, email_port)
                
                if email_use_tls:
                    server.starttls()
                
                server.login(email_host_user, email_host_password)
                server.quit()
                
                return JsonResponse({
                    'success': True,
                    'message': f'✓ SMTP connection successful! Connected to {email_host}:{email_port}'
                })
                
            except smtplib.SMTPAuthenticationError:
                return JsonResponse({
                    'success': False,
                    'message': 'Authentication failed. Check email address and app password.'
                })
            except smtplib.SMTPException as e:
                return JsonResponse({
                    'success': False,
                    'message': f'SMTP Error: {str(e)}'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Connection failed: {str(e)}'
                })
                
        except Exception as e:
            logger.error(f"SMTP test error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })


@method_decorator(login_required, name='dispatch')
class SaveSMTPSettingsView(View):
    """Save SMTP settings to environment or configuration"""
    
    def post(self, request):
        try:
            # Only admin users can change settings
            if not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'message': 'You do not have permission to change SMTP settings.'
                })
            
            email_backend = request.POST.get('email_backend', 'django.core.mail.backends.console.EmailBackend')
            email_host = request.POST.get('email_host', 'smtp.gmail.com')
            email_port = request.POST.get('email_port', '587')
            email_use_tls = request.POST.get('email_use_tls') == 'on'
            email_host_user = request.POST.get('email_host_user', '')
            default_from_email = request.POST.get('default_from_email', '')
            email_host_password = request.POST.get('email_host_password', '')
            
            # Validate required fields
            if 'smtp' in email_backend and (not email_host_user or not email_host_password):
                return JsonResponse({
                    'success': False,
                    'message': 'Email address and app password are required for SMTP.'
                })
            
            # Update Django settings dynamically
            settings.EMAIL_BACKEND = email_backend
            settings.EMAIL_HOST = email_host
            settings.EMAIL_PORT = int(email_port)
            settings.EMAIL_USE_TLS = email_use_tls
            settings.EMAIL_HOST_USER = email_host_user
            settings.EMAIL_HOST_PASSWORD = email_host_password
            settings.DEFAULT_FROM_EMAIL = default_from_email
            
            logger.info(f"SMTP settings updated by {request.user.username}")
            logger.info(f"Email Host: {email_host}:{email_port}")
            logger.info(f"From Email: {default_from_email}")
            
            return JsonResponse({
                'success': True,
                'message': 'SMTP settings saved successfully!'
            })
            
        except Exception as e:
            logger.error(f"Error saving SMTP settings: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error saving settings: {str(e)}'
            })
