from django import forms


class select_excel_columns_form(forms.Form):
    def __init__(self, *args, **kwargs):
        try:
            columns = kwargs.pop('columns')
            choices = kwargs.pop('choices')
        except KeyError:
            columns = {}
            choices = []

        super().__init__(*args, **kwargs)
        for key in columns.keys():
            self.fields['column-' + key] = forms.ChoiceField(
                required=False,
                widget=forms.Select(attrs={
                    'class': 'form-select',
                    'id': 'column-' + key,
                    'style': 'overflow-y: scroll;'
                }),
                choices=choices
            )
