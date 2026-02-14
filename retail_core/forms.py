"""
Admin forms for the retail platform.
"""

from django import forms
from products.models import Product
from inventory.models import InventoryLevel
from alerts.models import Alert


class ProductForm(forms.ModelForm):
    """Custom form for Product admin."""
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        cost_price = cleaned_data.get('cost_price')
        selling_price = cleaned_data.get('selling_price')
        
        if cost_price and selling_price and selling_price < cost_price:
            raise forms.ValidationError(
                "Selling price cannot be less than cost price."
            )
        
        return cleaned_data


class InventoryLevelForm(forms.ModelForm):
    """Custom form for InventoryLevel admin."""
    
    class Meta:
        model = InventoryLevel
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity_on_hand')
        reserved = cleaned_data.get('quantity_reserved')
        
        if quantity and reserved and reserved > quantity:
            raise forms.ValidationError(
                "Reserved quantity cannot exceed on-hand quantity."
            )
        
        return cleaned_data


class AlertActionForm(forms.Form):
    """Form for alert actions."""
    
    ACTION_CHOICES = [
        ('acknowledge', 'Acknowledge'),
        ('resolve', 'Resolve'),
        ('escalate', 'Escalate'),
    ]
    
    action = forms.ChoiceField(choices=ACTION_CHOICES)
    notes = forms.CharField(widget=forms.Textarea, required=False)
