from django import forms
from django.core.exceptions import ValidationError


class search_client_form(forms.Form):
    

    cedula = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "search-cedula",
                "placeholder": "cedula",
                "autocomplete": "off",
            }
        ),
    )

    celular = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "search-celular",
                "placeholder": "celular",
                "autocomplete": "off",
            }
        ),
    )

    nombres = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "search-nombres",
                "placeholder": "nombres",
                "autocomplete": "off",
            }
        ),
    )

    apellidos = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "search-apellidos",
                "placeholder": "apellidos",
                "autocomplete": "off",
            }
        ),
    )

        
    