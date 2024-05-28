from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError
from ..utils.database.typesData import LIST_CIUDAD
from django.core.validators import RegexValidator

def checkCedula(value:str):
  if not value.isdigit():
    raise forms.ValidationError("Ingresar solo numeros.")
  if len(value) != 10:
    raise forms.ValidationError("Ingrese una identificación correcta.")
  

class BaseFormLeads(forms.Form):
    nombre = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Nombre",
            "id": "lead-nombre"
        })
    )
    
    apellido = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Apellido",
            "id": "lead-apellido"
        })
    )
    
    cedula = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Cédula",
            "id": "lead-cedula"
        }),
        validators=[checkCedula],
    )

    operador = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-operador",
        })
    )

    celular = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Celular",
            "id": "lead-celular"
        }),
        validators=[RegexValidator(r'^\d{10}$', 'El número de teléfono debe contener exactamente 10 dígitos.')], 
    )

    telefono = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Telefono",
            "id": "lead-telefono"
        }),
        validators=[RegexValidator(r'^\d{10}$', 'El número de teléfono debe contener exactamente 10 dígitos.')], 
        max_length=10       
    )

    valor_facturado_entero = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Entero",
            "id": "lead-valorEmtero"
        })
    )

    valor_facturado_decimal = forms.DecimalField(
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Decimal",
            "id": "lead-valorDecimal"
        })
    )
    correo = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Correo",
            "id": "lead-correo"
        })
    )

    Iva = forms.ChoiceField(
        required=True,        
        choices=[ ('15', 'Iva 15%')],
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-iva",
        })
    )

    """
    Iva = forms.ChoiceField(
        required=True,        
        choices=[ ('15', 'Iva 15%'), ('12', 'Iva 12%')],
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-iva",
            "readonly": True
        })
    )
    """



class create_form_pycca(BaseFormLeads):

    compania = forms.CharField(widget=forms.HiddenInput(attrs={
            "class": "form-control",
            "id": "lead-compania"
        }), initial="PYCCA", required=False)


    campana = forms.ChoiceField(
        required=True,
        choices=[('1', 'TELEVENTA'), ('2', 'CAPTACION')],
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-campana"
        })
    )

    subcampana = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-subcampana"
        })
    )

    producto = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-producto"
        })
    )

    descripcion = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Ingresa la descripción del producto",
            "id": "lead-descripcion"
        })
    )

    CIUDAD_RANGE = [(ciudad, ciudad) for ciudad in LIST_CIUDAD if ciudad != "ALL"]        

    ciudad = forms.ChoiceField(
        required=True,
        choices=CIUDAD_RANGE,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "lead-ciudad",
            },
        ),
    )

    tipo_venta = forms.ChoiceField(
        required=True,
        choices=[('VENTA BASE ANTERIOR', 'VENTA BASE ANTERIOR'), ('VENTA BASE ACTUAL', 'VENTA BASE ACTUAL'), ('VENTA CLIENTE REFERIDO', 'VENTA CLIENTE REFERIDO')],
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-tipoVenta"
        })
    )

    acepta_seguro = forms.ChoiceField(
        required=True,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-seguro"
        })
    )

    def __init__(self, *args, **kwargs):
        list_productos = kwargs.pop('list_productos', None)
        list_subcampanas = kwargs.pop('list_subcampanas', None)
        list_operador = kwargs.pop('list_operador', None)
        initial_values = kwargs.pop('initial_values', None)
        super().__init__(*args, **kwargs)
        
        self.fields['producto'].choices = list_productos if list_productos else []

        self.fields['subcampana'].choices = list_subcampanas if list_subcampanas else []           

        self.fields['operador'].choices = list_operador if list_operador else []  
        #self.fields['operador'].widget.attrs['readonly'] = 'readonly'

        if initial_values:
            self.initial.update(initial_values)

    
class create_form_laica(BaseFormLeads):
    compania = forms.CharField(widget=forms.HiddenInput(attrs={
            "class": "form-control",
            "id": "lead-compania"
        }), initial="Laica", required=False)

    campana = forms.ChoiceField(
        required=True,
        choices=[('8', 'LAICA')],
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-campana",
        })
    )

    subcampana = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-subcampana"
        })
    )

    fecha_1stContact = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "id": "lead-fecha1contacto",
                "placeholder": "Fecha de Compra",
                "type": "date",
            },
        ),
    )

    facultad = forms.ChoiceField(
        required=True,
        choices=[('FADM', 'FADM'), ('FCSD', 'FCSD'), ('FEDU', 'FEDU'), ('FIIC', 'FIIC')],
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-facultad"
        })
    )

    carrera = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Carrera",
            "id": "lead-carrera"
        })
    )

    modalidad = forms.ChoiceField(
        required=True,
        choices=[('HIBRIDO', 'HIBRIDO'), ('ON LINE', 'ON LINE'), ('PRESENCIAL', 'PRESENCIAL')],
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-modalidad"
        })
    )

    def __init__(self, *args, **kwargs):
        list_subcampanas = kwargs.pop('list_subcampanas', None)
        list_operador = kwargs.pop('list_operador', None)
        initial_values = kwargs.pop('initial_values', None)
        super().__init__(*args, **kwargs)

        self.fields['subcampana'].choices = list_subcampanas  if list_subcampanas else []

        self.fields['operador'].choices = list_operador if list_operador else []  


        if initial_values:
            self.initial.update(initial_values)
    
    
    
class create_form_cnt(BaseFormLeads):
    id = forms.IntegerField(widget=forms.HiddenInput(), initial="cnt", required=False)

    fecha_activacion = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "id": "lead-fechaActivacion",
                "placeholder": "Fecha de Activacion",
                "type": "date",
            },
        ),
    )
    
    sistema = forms.CharField(
        widget=forms.HiddenInput(), 
        required=False,
        initial="SMARTFLEX"
    )
    
    digitador = forms.CharField(
        widget=forms.HiddenInput(), 
        required=False,
        initial="Gina"
    )
    
    
    SUPERVISOR_CHOICES = [
        ('Nicolle', 'Nicolle'),
        ('Gustavo', 'Gustavo'),
    ]
    
    supervisor = forms.ChoiceField(
        required=True,
        choices=SUPERVISOR_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-supervisor"
        })
    )
    
    ASESOR_CHOICES = [
        ('GINA LINDAO ONTANEDA','GINA LINDAO ONTANEDA' ),
        ('GEOMAYRA ZAMBRANO MENDOZA ', 'GEOMAYRA ZAMBRANO MENDOZA '),
        ('MA.TERESA ARIZALA MOSQUERA', 'MA.TERESA ARIZALA MOSQUERA'),
    ]
    
    asesor = forms.ChoiceField(
        required=True,
        choices=ASESOR_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-asesor"
        })
    )
    
    
    valor_facturado_entero = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Entero",
            "id": "lead-valorEmtero"
        })
    )

    valor_facturado_decimal = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Decimal",
            "id": "lead-valorDecimal"
        })
    )
    
    cbm_entero = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Entero",
            "id": "lead-cbmEntero"
        })
    )
    
    cbm_decimal = forms.DecimalField(
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Decimal",
            "id": "lead-cbmDecimal"
        })
    )
    
    tb2_entero = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Entero",
            "id": "lead-tb2Entero"
        })
    )
    
    tb2_decimal = forms.DecimalField(
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Decimal",
            "id": "lead-tb2Decimal"
        })
    )
    
    
   
    
    simcard = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Simcard",
            "id": "lead-simcard"
        })
    )
    
    usuario_smartflex = forms.CharField(
        widget=forms.HiddenInput(), 
        required=False,
        initial="emontiel"
    )
    
    codigo = forms.CharField(
        widget=forms.HiddenInput(), 
        required=False,
        initial="19578"
    )
    
    contrato = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Contrato",
            "id": "lead-contrato"
        })
    )
    
    imei = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Imei",
            "id": "lead-imei"
        })
    )
    
    equipo = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Equipo",
            "id": "lead-equipo"
        })
    )
    
    CICLO_CHOICES = [
        ('CICLO 1-7', 'CICLO 1-7'),
        ('CICLO 8-15', 'CICLO 8-15'),
        ('CICLO 16-22', 'CICLO 16-22'),
        ('CICLO 23-31', 'CICLO 23-31'),
    ]
    
    ciclo_facturacion = forms.ChoiceField(
        required=True,
        choices=CICLO_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-cicloFacturacion"
        })
    )
    
    secuencia_sre = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Secuencia SRE",
            "id": "lead-secuenciaSre"
        })
    )
    
    ESTADO_LEGAL_CHOICES = [
        ('NO LEGALIZADO POR CNT', 'NO LEGALIZADO POR CNT'),
        ('LEGALIZADO POR CNT', 'LEGALIZADO POR CNT'),
    ]
    
    legalizacion_cnt = forms.ChoiceField(
        required=True,
        choices=ESTADO_LEGAL_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-legalizacionCnt"
        })
    )
        
    entregado_cnt = forms.ChoiceField(
        required=True,
        choices=[('SI', 'Sí'), ('NO', 'No')],
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-entregadoCnt"
        })
    )
    
    PLAN_CHOICES = [
        ('ULTRANAVEGACION PLAN 17,99', 'ULTRANAVEGACION PLAN 17,99'),
        ('PLAN ILIMITADO SOCIAL PLUS $21.99', 'PLAN ILIMITADO SOCIAL PLUS $21.99'),
        ('PLAN PORTABILIDAD $12.99', 'PLAN PORTABILIDAD $12.99'),
        
    ]
    
    plan = forms.ChoiceField(
        required=True,
        choices=PLAN_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-plan"
        })
    )

    observacion = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Ingresa la observacion",
            "id": "lead-observacion"
        })
    ) 
    
    TIPO_CHOICES = [
        ('PORT POS', 'PORT POS'),
        ('CAMBIO DE PLAN', 'CAMBIO DE PLAN'),
        ('PORT PRE', 'PORT PRE'),
        ('LINEA NUEVA', 'LINEA NUEVA'),
    ]

    tipo = forms.ChoiceField(
        required=True,
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-tipo"
        })
    )
    
    SOLICITUD_CHOICES = [
        ('NEGADA', 'NEGADA'),
        ('VENTA', 'VENTA'),
    ]
    
    solicitud = forms.ChoiceField(
        required=True,
        choices=SOLICITUD_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-solicitud"
        })
    )
    
    ESTADO_CHOICES = [
        ('BONO', 'BONO'),
        ('ACTIVA', 'ACTIVA'),
        ('DESISTE DEL SERVICIO', 'DESISTE DEL SERVICIO'),   
    ]
    
    estado = forms.ChoiceField(
        required=True,
        choices=ESTADO_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-estado"
        })
    )
    
    subcampana = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Subcampana",
            "id": "lead-subcampana"
        })
    ) 
    


    def __init__(self, *args, **kwargs):
        initial_values = kwargs.pop("initial_values", None)
        super().__init__(*args, **kwargs)

        if initial_values:
            self.initial.update(initial_values)


class create_form_zurich(BaseFormLeads):
    compania = forms.CharField(widget=forms.HiddenInput(attrs={
            "class": "form-control",
            "id": "lead-compania"
        }), initial="Zurich", required=False)
    
    asegurado = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Nombres completos",
            "id": "lead-asegurado"
        })
    )

    CHOICES_GENERO = [("MASCULINO", "Masculino"), ("FEMENINO", "Femenino")] 
    genero = forms.ChoiceField(
        required=True,
        choices=CHOICES_GENERO,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "lead-genero"
        })
    )

    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "id": "lead-nacimiento",
                "placeholder": "Fecha de nacimiento",
                "type": "date",
            },
        ),
    )

    CIUDAD_RANGE = [(ciudad, ciudad) for ciudad in LIST_CIUDAD if ciudad != "ALL"]        

    ciudad = forms.ChoiceField(
        required=True,
        choices=CIUDAD_RANGE,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "lead-ciudad",
            },
        ),
    )

    #INICIO DE VIGENCIA ES LA FECHA ACTUAL

    
    fecha_vencimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "id": "lead-vencimiento",
                "placeholder": "Fecha de vencimiento",
                "type": "date",
            },
        ),
    )

    direccion = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Direccion",
            "id": "lead-direccion"
        })
    )

    codigoAsesor = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Codigo",
            "id": "lead-codigoAsesor"
        })
    )

    valorAegurado = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Valor asegurado",
            "id": "lead-valorAegurado"
        })
    )

    valorNeto = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Valor neto",
            "id": "lead-valorNeto"
        })
    )

    actEconomica = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej.: Electricista",
            "id": "lead-actEconomica"
        })
    )

    producto = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Producto",
            "id": "lead-producto"
        })
    )

    plan = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Tipo de plan",
            "id": "lead-plan"
        })
    )


