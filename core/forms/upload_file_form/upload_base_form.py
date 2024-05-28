from django import forms
from django.core.validators import FileExtensionValidator


class upload_base_form(forms.Form):
    file = forms.FileField(
        required=True,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control form-control-sm',
                'id': 'formFileSm',
                'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel'
            }
        ),
        validators=[FileExtensionValidator(
            allowed_extensions=['xlsx', 'xlsm', 'xlsb', 'xls'])]
    )

    """
    def __init__(self, *args, **kwargs):
        try:
            choices = kwargs.pop('choices_list')
        except KeyError:
            choices = []

        super().__init__(*args, **kwargs)
        self.fields['choices'].choices = choices
    """