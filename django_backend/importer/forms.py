"""Django forms for importer app."""
from django import forms
from .models import Product, Webhook


class ProductForm(forms.ModelForm):
    """Product form."""
    class Meta:
        model = Product
        fields = ['sku', 'name', 'description', 'price', 'quantity', 'active']
        widgets = {
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter SKU',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter description',
                'rows': 3
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter price',
                'step': '0.01'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter quantity'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class WebhookForm(forms.ModelForm):
    """Webhook form."""
    class Meta:
        model = Webhook
        fields = ['url', 'event_type', 'active']
        widgets = {
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/webhook',
                'required': True
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class CSVUploadForm(forms.Form):
    """CSV upload form."""
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv',
            'required': True
        }),
        help_text='Upload a CSV file with columns: sku, name, description, price, quantity'
    )
