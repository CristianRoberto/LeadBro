from django import forms
from django.core.exceptions import ValidationError


class create_customer_form(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'customer-name',
        'placeholder': 'Nombre'
    }))

    contact_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'contact-name',
        'placeholder': 'Contacto'
    }))

    contact_phone = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'contact-phone',
        'placeholder': 'Teléfono'
    }))

    contact_email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'id': 'contact-email',
        'placeholder': 'Correo'
    }))

    id = forms.IntegerField(widget=forms.HiddenInput(), initial=None, required=False)
