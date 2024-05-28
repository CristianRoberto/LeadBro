from django import forms
from django.core.exceptions import ValidationError


class sync_google_sheet_form(forms.Form):
    spreadsheet_id = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'spreadheet-id',
        'placeholder': 'id de archivo'
    }))

    spreadsheet_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'spreadheet-name',
        'placeholder': 'Nombre de archivo'
    }))

    cutting_time_range = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'cutting-time-range',
        'placeholder': 'ej: 09:30, 18:00'
    }))
