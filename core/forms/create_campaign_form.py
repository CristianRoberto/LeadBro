
from django import forms


class create_campaign_form(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'campaign-name',
        'placeholder': 'Nombre'
    }))

    customers = forms.ChoiceField(required=True, widget=forms.Select(attrs={
        'class': 'form-control',
        'id': 'customers-list'
    }))

    id = forms.IntegerField(widget=forms.HiddenInput(),
                            initial=None, required=False)

    def __init__(self, *args, **kwargs):
        try:
            choices = kwargs.pop('customers_list')
        except KeyError:
            choices = []
            
        super().__init__(*args, **kwargs)

        self.fields['customers'].choices = choices
