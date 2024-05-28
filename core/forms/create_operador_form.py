from django import forms
from django.core.exceptions import ValidationError
from django.core import validators



def checkCedula(value:str):
  if not value.isdigit():
    raise forms.ValidationError("Ingresar solo numeros.")
  if len(value) != 10:
    raise forms.ValidationError("Ingrese una identificación correcta.")
  

class base_operador_form(forms.Form):
    
    
    nombres = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "operador-nombres",
                "placeholder": "nombres",
                "autocomplete": "off",
            }
        ),        
        validators= [validators.MaxLengthValidator(50), validators.RegexValidator('^[A-Za-z ]+$')]
    )

    apellidos = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "operador-apellidos",
                "placeholder": "apellidos",
                "autocomplete": "off",
            }
        ),
        validators= [validators.MaxLengthValidator(50), validators.RegexValidator('^[A-Za-z ]+$')]

    )

    cedula = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "operador-cedula",
                "placeholder": "cedula",
                "autocomplete": "off",
            }
        ),
        validators=[checkCedula]
    )
 
    
    codigoDinomi = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "id": "operador-codigoDinomi",
                "placeholder": "codigo",
                "autocomplete": "off",
            },
        ),
    )

    lideres = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "operador-lider"
        })
    )

    
    id = forms.IntegerField(widget=forms.HiddenInput(), initial=None, required=False)


    def __init__(self, *args, **kwargs):
        list_lideres = kwargs.pop('list_lideres', None)
        initial_values = kwargs.pop('initial_values', None)
        super().__init__(*args, **kwargs)

        self.fields['lideres'].choices = list_lideres  if list_lideres else []  

        if initial_values:
            self.initial.update(initial_values)



class create_operador_form(base_operador_form):
    correo = forms.EmailField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "operador-correo",
                "placeholder": "Ingrese su correo",
            }
        ),
    )

    password = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "operador-password",
                "placeholder": "Ingrese contraseña",  
                "autocomplete": "off",
            }
        ),        
        validators= [validators.MaxLengthValidator(20)]
    )

    def __init__(self, *args, **kwargs):
        list_lideres = kwargs.pop('list_lideres', None)
        initial_values = kwargs.pop('initial_values', None)
        super().__init__(*args, **kwargs)

        self.fields['lideres'].choices = list_lideres  if list_lideres else []  
        
        if initial_values:
            self.initial.update(initial_values)


class edit_operador_form(forms.Form):

    id = forms.IntegerField(widget=forms.HiddenInput(), initial=None, required=False)


    compania = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "operador-compania"
        })
    )
    campana = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "operador-campana",
        })
    )
    
    def __init__(self, *args, **kwargs):
        list_companias = kwargs.pop('list_companias', None)
        list_campanas = kwargs.pop('list_campanas', None)
        list_historial_newRegister = kwargs.pop("list_historial_newRegister", None)
        #list_historial = kwargs.pop('list_historial', None)
        initial_values = kwargs.pop('initial_values', None)
        super().__init__(*args, **kwargs)
        
        self.fields['compania'].choices = list_companias if list_companias else []
        self.fields['campana'].choices = list_campanas if list_campanas else []

        if list_historial_newRegister:
            for i in list_historial_newRegister:  
                self.fields[f"historialId{i}"] = forms.IntegerField(
                    required=False,
                    widget=forms.HiddenInput(
                        attrs={
                            "class": "form-control",
                            "id": f"historialId{i}",
                            "readonly": "readonly"
                        }
                    ),
                    initial= 0
                )

                self.fields[f"historialCampana{i}"] = forms.CharField(
                    required=True,
                    widget=forms.TextInput(
                        attrs={
                            "class": "form-control",
                            "id": f"historialCampana{i}",
                            "placeholder": "Campaña",
                            "readonly": "readonly"
                        }
                    ),                    
                )

                self.fields[f"historialCuota{i}"] = forms.IntegerField(
                    required=True,
                    widget=forms.NumberInput(
                        attrs={
                            "class": "form-control",
                            "id": f"historialCuota{i}",
                        }
                    ),
                )

                self.fields[f"historialFecha{i}"] = forms.DateField(
                    required=True,
                    widget=forms.DateInput(
                        attrs={
                            "class": "form-control",
                            "id": f"historialFecha{i}",
                            "placeholder": "Fecha de registro",
                            "type": "date",
                            "readonly": "readonly"
                        },
                    ),                    
                )

        if initial_values:
            self.initial.update(initial_values)