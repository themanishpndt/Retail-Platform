"""
Django models for retail_core app
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import secrets


class PasswordResetOTP(models.Model):
    """Model to store temporary OTP for password reset"""
    
    email = models.EmailField(db_index=True)
    otp = models.CharField(max_length=4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'expires_at']),
            models.Index(fields=['is_used', 'expires_at']),
        ]
    
    def __str__(self):
        return f"OTP for {self.email} - Created: {self.created_at}"
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is valid and not expired/used"""
        return not self.is_used and not self.is_expired()
    
    @staticmethod
    def generate_otp():
        """Generate a random 4-digit OTP"""
        return str(secrets.randbelow(10000)).zfill(4)
    
    @staticmethod
    def create_otp(email, user=None, expires_in_minutes=10):
        """Create a new OTP for the given email"""
        # Invalidate previous OTPs
        PasswordResetOTP.objects.filter(
            email=email,
            is_used=False,
            expires_at__gt=timezone.now()
        ).update(is_used=True)
        
        otp_code = PasswordResetOTP.generate_otp()
        otp = PasswordResetOTP.objects.create(
            email=email,
            otp=otp_code,
            user=user,
            expires_at=timezone.now() + timedelta(minutes=expires_in_minutes)
        )
        return otp
    
    @staticmethod
    def verify_otp(email, otp_code):
        """Verify OTP and return the OTP object if valid"""
        try:
            otp = PasswordResetOTP.objects.get(
                email=email,
                otp=otp_code,
                is_used=False
            )
            
            if otp.is_expired():
                return None
            
            return otp
        except PasswordResetOTP.DoesNotExist:
            return None
