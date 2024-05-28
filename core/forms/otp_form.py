from django import forms
from django.core.exceptions import ValidationError


class otp_form(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        label="Código OTP",
        widget=forms.TextInput(attrs={"autocomplete": "off", "class": "form-control"}),
    )

    """
    email_notification = forms.BooleanField(
        label="Notificar acceso",
        required=True,
        widget=forms.HiddenInput(),  # Esto convierte el campo en oculto
        initial=False  # Esto establece el valor inicial del campo
    )

    def __init__(self, *args, **kwargs):
        initial_values = kwargs.pop("initial_values", None)
        super().__init__(*args, **kwargs)

        if initial_values:
            self.initial.update(initial_values)

    """