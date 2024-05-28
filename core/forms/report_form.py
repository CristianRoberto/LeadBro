from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import calendar
import datetime

# Custom date validator
def validate_date(value):
    try:
        # Try to convert the value into a date.
        # If the date is invalid, it will raise a ValueError
        datetime.datetime.strptime(value, f'%Y-%m-%d')
    except ValueError:
        raise ValidationError('Invalid date: Ensure the day is correct for the given month and year.')

class ReportForm(forms.Form):
    
    # Fields for the initial date
    current_year = datetime.datetime.now().year

    # Fields for the initial date
    start_year = forms.ChoiceField(
        choices=[(y, y) for y in range(current_year - 20, current_year + 21)],
        label='Año Inicial',
        initial=current_year
    )
    start_month = forms.ChoiceField(
        choices=[(str(m), calendar.month_name[m]) for m in range(1, 13)],
        label='Mes Inicial'
    )
    start_day = forms.ChoiceField(
        choices=[(d, d) for d in range(1, 32)],
        label='Día Inicial'
    )

    # Fields for the final date
    end_year = forms.ChoiceField(
        choices=[(y, y) for y in range(current_year - 20, current_year + 21)],
        label='Año Final',
        initial=current_year
    )
    end_month = forms.ChoiceField(
        choices=[(str(m), calendar.month_name[m]) for m in range(1, 13)],
        label='Mes Final'
    )
    end_day = forms.ChoiceField(
        choices=[(d, d) for d in range(1, 32)],
        label='Día Final'
    )
    
    # Choice field with three options
    OPTIONS = (
        ('outgoing', 'Outgoing'),
        ('incoming', 'Incoming'),
        ('manualdialing', 'Manualdialing'),
    )
    tipo = forms.ChoiceField(label='Tipo', choices=OPTIONS)

    # Alphanumeric field
    # alphanumeric_validator = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
    alphanumeric_validator = RegexValidator(r'^[0-9a-zA-Z ]*$', 'Only alphanumeric characters and spaces are allowed.')
    campania = forms.CharField(label='Campana', # validators=[alphanumeric_validator]
                               )

    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get("start_year")
        start_month = cleaned_data.get("start_month")
        start_day = cleaned_data.get("start_day")
        end_year = cleaned_data.get("end_year")
        end_month = cleaned_data.get("end_month")
        end_day = cleaned_data.get("end_day")

        # Validate and combine into single dates
        try:
            start_date = datetime.date(int(start_year), int(start_month), int(start_day))
            end_date = datetime.date(int(end_year), int(end_month), int(end_day))
            cleaned_data['start_date'] = start_date
            cleaned_data['end_date'] = end_date

            # Check if the end date is after the start date
            if end_date < start_date:
                raise ValidationError('End date must be after start date.')
        except ValueError:
            raise ValidationError('Invalid date: Ensure the day is correct for the given month and year.')

        return cleaned_data
