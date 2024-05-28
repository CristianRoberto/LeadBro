from django import forms

class CreateSubCampaignForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'campaign-name',
        'placeholder': 'Nombre'
    }))

    listacampana = forms.ChoiceField(required=True, widget=forms.Select(attrs={
        'class': 'form-control',
        'id': 'campaign-list'
    }))

    customers = forms.ChoiceField(
        required=False,  # Cambia a False para permitir omisión al actualizar
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'customers-list',
            'readonly': 'readonly'
        })
    )

    id = forms.IntegerField(widget=forms.HiddenInput(), initial=None, required=False)

    def __init__(self, *args, **kwargs):
        customers_choices = kwargs.pop('customers_list', [])
        campaigns_choices = kwargs.pop('campaigns_list', [])
        is_update = kwargs.pop('is_update', False)  # Indicador para saber si es actualización

        super().__init__(*args, **kwargs)
        self.fields['customers'].choices = customers_choices
        self.fields['listacampana'].choices = campaigns_choices

        if is_update:
            self.fields['customers'].required = False  # Hacer que no sea obligatorio al actualizar
        else:
            self.fields['customers'].required = True  # Es obligatorio al crear
