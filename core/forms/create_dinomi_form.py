from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime


class create_dinomi_form(forms.Form):

    startDate = forms.DateField(
        required=True,
        #input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(
            #format="%Y-%m-%d",
            attrs={
                "class": "form-control",
                "id": "dinomi-startDate",
                "placeholder": "Selecciona una fecha",
                "type": "date",
            },
        ),
    )

    endDate = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "id": "dinomi-endDate",
                "placeholder": "Selecciona una fecha",
                "type": "date",
            },
        ),
    )

    TIPO_DINOMI = [
        ("outgoing", "OUTGOING"),
        ("incoming", "INCOMING"),
        ("manualdialding", "MANUALDIALDING"),
    ]

    tipo = forms.ChoiceField(
        required=True,
        choices=TIPO_DINOMI,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "dinomi-tipo",
            },
        ),
    )

    nombre_dinomi = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "dinomi-nombre",
                "placeholder": "Nombre",
            }
        ),
    )

    equipo_dinomi = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "dinomi-equipo",
                "placeholder": "Equipo",
            }
        ),
    )

    ESTADO_DINOMI = [
        ("detenido", "DETENIDO"),
        ("activo", "ACTIVO"),
    ]

    estado_dinomi = forms.ChoiceField(
        required=False,
        initial="ACTIVO",
        choices=ESTADO_DINOMI,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "dinomi-estado",
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        initial_values = kwargs.pop("initial_values", None)
        super().__init__(*args, **kwargs)

        ATRIBUTO_TIPO_CHOICES = [
            ("cedula", "cedula"),
            ("Nombres Completos", "Nombres Completos"),
            ("Nombres", "Nombres"),
            ("Apellidos", "Apellidos"),
            ("telefono", "telefono"),
            ("celular", "celular"),
            ("cupo_pycca", "cupo_pycca"),
            ("correo", "correo"),
        ]

        for i in range(1, 6):  # Por ejemplo, para añadir 5 campos
            self.fields[f"atributo_nombre_{i}"] = forms.CharField(
                required=False,
                widget=forms.TextInput(
                    attrs={
                        "autocomplete": "off",
                        "class": "form-control",
                        "placeholder": "Ingrese el nombre del atributo",
                    }
                ),
            )

            self.fields[f"atributo_tipo_{i}"] = forms.ChoiceField(
                required=False,
                choices=ATRIBUTO_TIPO_CHOICES,
                widget=forms.Select(
                    attrs={
                        "class": "form-control",
                    }
                ),
            )

        if initial_values:
            self.initial.update(initial_values)
