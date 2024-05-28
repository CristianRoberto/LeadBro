from django import forms


class EditClienteForm(forms.Form):
    cedula = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "client-cedula",
                "placeholder": "Cédula",
            }
        ),
    )
    nombres = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "client-nombres",
                "placeholder": "Nombres",
            }
        ),
    )
    apellidos = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "client-apellidos",
                "placeholder": "Apellidos",
            }
        ),
    )
    fecha_nacimiento = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "id": "client-fecha-nacimiento",
                "placeholder": "Fecha de Nacimiento",
            }
        ),
    )
    edad = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "client-edad",
                "placeholder": "Edad",
            }
        ),
    )
    genero = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "client-genero",
                "placeholder": "Género",
            }
        ),
    )
    ciudad = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "client-ciudad",
                "placeholder": "Ciudad",
            }
        ),
    )
    id = forms.IntegerField(widget=forms.HiddenInput(), required=True)

    def __init__(self, *args, **kwargs):
        initial_values = kwargs.pop('initial_values', None)
        super().__init__(*args, **kwargs)
        
        if initial_values:
            self.initial.update(initial_values)
