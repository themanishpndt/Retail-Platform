"""
Authentication Middleware
Handles session management, timeout warnings, and security features
"""

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class SessionTimeoutMiddleware(MiddlewareMixin):
    """
    Middleware to handle session timeout
    Logs out users after a period of inactivity
    """
    
    TIMEOUT_MINUTES = 30  # Session timeout in minutes
    WARNING_MINUTES = 5   # Show warning 5 minutes before timeout
    
    def process_request(self, request):
        """Process each request to check session timeout"""
        
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            return None
        
        # Skip for certain URLs
        skip_urls = [
            reverse('admin:logout'),
            reverse('admin:login'),
            '/api/',
            '/static/',
            '/media/',
        ]
        
        if any(request.path.startswith(url) for url in skip_urls):
            return None
        
        # Get last activity time
        now = timezone.now()
        last_activity = request.session.get('last_activity')
        
        if last_activity:
            last_activity = timezone.make_aware(
                timezone.datetime.fromisoformat(last_activity)
            )
            elapsed = (now - last_activity).total_seconds() / 60
            
            # Check if session has timed out
            if elapsed > self.TIMEOUT_MINUTES:
                logger.warning(
                    f"Session timeout: {request.user.username} - "
                    f"Inactive for {elapsed:.0f} minutes"
                )
                logout(request)
                return redirect(f"{reverse('admin:login')}?timeout=1")
            
            # Show warning if approaching timeout
            if elapsed > (self.TIMEOUT_MINUTES - self.WARNING_MINUTES):
                request.session['session_warning'] = True
        
        # Update last activity time
        request.session['last_activity'] = now.isoformat()
        
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses
    """
    
    def process_response(self, request, response):
        """Add security headers"""
        
        # Prevent clickjacking
        response['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Prevent MIME sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net fonts.googleapis.com; "
            "font-src 'self' cdnjs.cloudflare.com fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature Policy
        response['Permissions-Policy'] = (
            'accelerometer=(), '
            'camera=(), '
            'geolocation=(), '
            'gyroscope=(), '
            'magnetometer=(), '
            'microphone=(), '
            'payment=(), '
            'usb=()'
        )
        
        return response


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Log all user activities for audit purposes
    """
    
    def process_request(self, request):
        """Log incoming requests"""
        
        if request.user.is_authenticated:
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Log request details
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                logger.info(
                    f"API Request | User: {request.user.username} | "
                    f"Method: {request.method} | Path: {request.path} | "
                    f"IP: {ip}"
                )
        
        return None


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    Optional: Restrict admin access to specific IP addresses
    Configure in settings.ADMIN_IP_WHITELIST
    """
    
    def process_request(self, request):
        """Check if user's IP is whitelisted"""
        
        # Skip if feature is disabled
        from django.conf import settings
        if not getattr(settings, 'ENABLE_IP_WHITELIST', False):
            return None
        
        # Skip for non-admin paths
        if not request.path.startswith('/admin/'):
            return None
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Get whitelist from settings
        whitelist = getattr(settings, 'ADMIN_IP_WHITELIST', [])
        
        if whitelist and ip not in whitelist and request.user.is_authenticated:
            logger.warning(
                f"Access denied from non-whitelisted IP: {ip} | "
                f"User: {request.user.username}"
            )
            return redirect('admin:login')
        
        return None


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting for login attempts
    """
    
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 15 * 60  # 15 minutes in seconds
    
    def process_request(self, request):
        """Check rate limits"""
        
        # Only check login endpoint
        if request.path != reverse('admin:login'):
            return None
        
        if request.method != 'POST':
            return None
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Check rate limit using cache
        from django.core.cache import cache
        cache_key = f"login_attempts_{ip}"
        attempts = cache.get(cache_key, 0)
        
        if attempts >= self.MAX_LOGIN_ATTEMPTS:
            logger.warning(
                f"Login rate limit exceeded for IP: {ip} | "
                f"Attempts: {attempts}"
            )
            return redirect(f"{reverse('admin:login')}?rate_limit=1")
        
        return None


class UserAgentValidationMiddleware(MiddlewareMixin):
    """
    Validate user agent to prevent suspicious requests
    """
    
    SUSPICIOUS_AGENTS = [
        'bot',
        'crawler',
        'spider',
        'scraper',
        'curl',
        'wget',
    ]
    
    def process_request(self, request):
        """Validate user agent"""
        
        if not request.user.is_authenticated:
            return None
        
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        for agent in self.SUSPICIOUS_AGENTS:
            if agent in user_agent:
                logger.warning(
                    f"Suspicious user agent detected: {user_agent} | "
                    f"User: {request.user.username} | "
                    f"IP: {request.META.get('REMOTE_ADDR')}"
                )
                break
        
        return None
