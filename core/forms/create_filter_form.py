from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError


class create_filter_form(forms.Form):
     
    OLD_RANGE = [(x, x) for x in range(1, 71)]
    VENTA_RANGE = [
        (0, 0),
        (10, 10),
        (100, 100),
        (200, 200),
        (300, 300),
        (400, 400),
        (500, 500),
        (1000, 1000),
        (2000, 2000),
        (5000, 5000),
        (10000, 10000),
        (20000, 20000),
        (50000, 50000),
        (100000, 100000),
    ]
    CIUDAD_RANGE = [
        ("ALL", "ALL"),
        ("GUAYAQUIL", "GUAYAQUIL"),
        ("QUITO", "QUITO"),
        ("CUENCA", "CUENCA"),
        ("SANTO DOMINGO", "SANTO DOMINGO"),
        ("MACHALA", "MACHALA"),
        ("DURÁN", "DURÁN"),
        ("MANTA", "MANTA"),
        ("PORTOVIEJO", "PORTOVIEJO"),
        ("LOJA", "LOJA"),
        ("AMBATO", "AMBATO"),
        ("ESMERALDAS", "ESMERALDAS"),
        ("QUEVEDO", "QUEVEDO"),
        ("RIOBAMBA", "RIOBAMBA"),
        ("MILAGRO", "MILAGRO"),
        ("IBARRA", "IBARRA"),
        ("LA LIBERTAD", "LA LIBERTAD"),
        ("BABAHOYO", "BABAHOYO"),
        ("SANGOLQUÍ", "SANGOLQUÍ"),
        ("DAULE", "DAULE"),
        ("LATACUNGA", "LATACUNGA"),
        ("TULCÁN", "TULCÁN"),
        ("CHONE", "CHONE"),
        ("PASAJE", "PASAJE"),
        ("SANTA ROSA", "SANTA ROSA"),
        ("NUEVA LOJA", "NUEVA LOJA"),
        ("HUAQUILLAS", "HUAQUILLAS"),
        ("EL CARMEN", "EL CARMEN"),
        ("MONTECRISTI", "MONTECRISTI"),
        ("SAMBORONDÓN", "SAMBORONDÓN"),
        ("PUERTO FRANCISCO DE ORELLANA", "PUERTO FRANCISCO DE ORELLANA"),
        ("JIPIJAPA", "JIPIJAPA"),
        ("SANTA ELENA", "SANTA ELENA"),
        ("OTAVALO", "OTAVALO"),
        ("CAYAMBE", "CAYAMBE"),
        ("BUENA FE", "BUENA FE"),
        ("VENTANAS", "VENTANAS"),
        ("VELASCO IBARRA", "VELASCO IBARRA"),
        ("LA TRONCAL", "LA TRONCAL"),
        ("EL TRIUNFO", "EL TRIUNFO"),
        ("SALINAS", "SALINAS"),
        ("GENERAL VILLAMIL", "GENERAL VILLAMIL"),
        ("AZOGUES", "AZOGUES"),
        ("PUYO", "PUYO"),
        ("VINCES", "VINCES"),
        ("LA CONCORDIA", "LA CONCORDIA"),
        ("ROSA ZÁRATE", "ROSA ZÁRATE"),
        ("BALZAR", "BALZAR"),
        ("NARANJITO", "NARANJITO"),
        ("NARANJAL", "NARANJAL"),
        ("GUARANDA", "GUARANDA"),
        ("LA MANÁ", "LA MANÁ"),
        ("TENA", "TENA"),
        ("SAN LORENZO", "SAN LORENZO"),
        ("CATAMAYO", "CATAMAYO"),
        ("EL GUABO", "EL GUABO"),
        ("PEDERNALES", "PEDERNALES"),
        ("ATUNTAQUI", "ATUNTAQUI"),
        ("BAHÍA DE CARÁQUEZ", "BAHÍA DE CARÁQUEZ"),
        ("PEDRO CARBO", "PEDRO CARBO"),
        ("MACAS", "MACAS"),
        ("YAGUACHI", "YAGUACHI"),
        ("CALCETA", "CALCETA"),
        ("ARENILLAS", "ARENILLAS"),
        ("JARAMIJÓ", "JARAMIJÓ"),
        ("VALENCIA", "VALENCIA"),
        ("MACHACHI", "MACHACHI"),
        ("SHUSHUFINDI", "SHUSHUFINDI"),
        ("ATACAMES", "ATACAMES"),
        ("PIÑAS", "PIÑAS"),
        ("SAN GABRIEL", "SAN GABRIEL"),
        ("GUALACEO", "GUALACEO"),
        ("LOMAS DE SARGENTILLO", "LOMAS DE SARGENTILLO"),
        ("CAÑAR", "CAÑAR"),
        ("CARIAMANGA", "CARIAMANGA"),
        ("BAÑOS DE AGUA SANTA", "BAÑOS DE AGUA SANTA"),
        ("MONTALVO", "MONTALVO"),
        ("MACARÁ", "MACARÁ"),
        ("SAN MIGUEL DE SALCEDO", "SAN MIGUEL DE SALCEDO"),
        ("ZAMORA", "ZAMORA"),
        ("PUERTO AYORA", "PUERTO AYORA"),
        ("LA JOYA DE LOS SACHAS", "LA JOYA DE LOS SACHAS"),
        ("SALITRE", "SALITRE"),
        ("TOSAGUA", "TOSAGUA"),
        ("PELILEO", "PELILEO"),
        ("PUJILÍ", "PUJILÍ"),
        ("TABACUNDO", "TABACUNDO"),
        ("PUERTO LÓPEZ", "PUERTO LÓPEZ"),
        ("SAN VICENTE", "SAN VICENTE"),
        ("SANTA ANA", "SANTA ANA"),
        ("ZARUMA", "ZARUMA"),
        ("BALAO", "BALAO"),
        ("ROCAFUERTE", "ROCAFUERTE"),
        ("YANTZAZA", "YANTZAZA"),
        ("COTACACHI", "COTACACHI"),
        ("SANTA LUCÍA", "SANTA LUCÍA"),
        ("CUMANDÁ", "CUMANDÁ"),
        ("PALESTINA", "PALESTINA"),
        ("ALFREDO BAQUERIZO MORENO", "ALFREDO BAQUERIZO MORENO"),
        ("NOBOL", "NOBOL"),
        ("MOCACHE", "MOCACHE"),
        ("PUEBLOVIEJO", "PUEBLOVIEJO"),
        ("PORTOVELO", "PORTOVELO"),
        ("SUCÚA", "SUCÚA"),
        ("CANTON GUANO", "CANTON GUANO"),
        ("PÍLLARO", "PÍLLARO"),
        ("SIMÓN BOLÍVAR", "SIMÓN BOLÍVAR"),
        ("GUALAQUIZA", "GUALAQUIZA"),
        ("PAUTE", "PAUTE"),
        ("SAQUISILÍ", "SAQUISILÍ"),
        ("CNEL. MARCELINO MARIDUEÑA", "CNEL. MARCELINO MARIDUEÑA"),
        ("PAJÁN", "PAJÁN"),
        ("SAN MIGUEL", "SAN MIGUEL"),
        ("PUERTO BAQUERIZO MORENO", "PUERTO BAQUERIZO MORENO"),
        ("CATACOCHA", "CATACOCHA"),
        ("PALENQUE", "PALENQUE"),
        ("ALAUSÍ", "ALAUSÍ"),
        ("CALUMA", "CALUMA"),
        ("CATARAMA", "CATARAMA"),
        ("FLAVIO ALFARO", "FLAVIO ALFARO"),
        ("COLIMES", "COLIMES"),
        ("ECHEANDÍA", "ECHEANDÍA"),
        ("JAMA", "JAMA"),
        ("GRAL. ANTONIO ELIZALDE (BUCAY)", "GRAL. ANTONIO ELIZALDE (BUCAY)"),
        ("ISIDRO AYORA", "ISIDRO AYORA"),
        ("MUISNE", "MUISNE"),
        ("SANTA ISABEL", "SANTA ISABEL"),
        ("PEDRO VICENTE MALDONADO", "PEDRO VICENTE MALDONADO"),
        ("BIBLIÁN", "BIBLIÁN"),
        ("ARCHIDONA", "ARCHIDONA"),
        ("JUNÍN", "JUNÍN"),
        ("BABA", "BABA"),
        ("VALDEZ (LIMONES)", "VALDEZ (LIMONES)"),
        ("PIMAMPIRO", "PIMAMPIRO"),
        ("CAMILO PONCE ENRÍQUEZ", "CAMILO PONCE ENRÍQUEZ"),
        ("SAN MIGUEL DE LOS BANCOS", "SAN MIGUEL DE LOS BANCOS"),
        ("EL TAMBO", "EL TAMBO"),
        ("QUINSALOMA", "QUINSALOMA"),
        ("EL ÁNGEL", "EL ÁNGEL"),
        ("ALAMOR", "ALAMOR"),
        ("CHAMBO", "CHAMBO"),
        ("CHIMBO", "CHIMBO"),
        ("CELICA", "CELICA"),
        ("CHORDELEG", "CHORDELEG"),
        ("BALSAS", "BALSAS"),
        ("SARAGURO", "SARAGURO"),
        ("EL CHACO", "EL CHACO"),
        ("GIRÓN", "GIRÓN"),
        ("HUACA", "HUACA"),
        ("PICHINCHA", "PICHINCHA"),
        ("CHUNCHI", "CHUNCHI"),
        ("PALLATANGA", "PALLATANGA"),
        ("MARCABELÍ", "MARCABELÍ"),
        ("SÍGSIG", "SÍGSIG"),
        (
            "GRAL. LEONIDAS PLAZA GUTIÉRREZ (LIMÓN)",
            "GRAL. LEONIDAS PLAZA GUTIÉRREZ (LIMÓN)",
        ),
        ("URCUQUÍ", "URCUQUÍ"),
        ("LORETO", "LORETO"),
        ("RIOVERDE", "RIOVERDE"),
        ("ZUMBA", "ZUMBA"),
        ("PALORA", "PALORA"),
        ("MIRA", "MIRA"),
        ("EL PANGUI", "EL PANGUI"),
        ("PUERTO QUITO", "PUERTO QUITO"),
        ("BOLÍVAR", "BOLÍVAR"),
        ("SUCRE", "SUCRE"),
        ("CHILLANES", "CHILLANES"),
        ("QUERO", "QUERO"),
        ("GUAMOTE", "GUAMOTE"),
        ("CEVALLOS", "CEVALLOS"),
        ("ZAPOTILLO", "ZAPOTILLO"),
        ("VILLA LA UNIÓN (CAJABAMBA)", "VILLA LA UNIÓN (CAJABAMBA)"),
        ("SANTIAGO DE MÉNDEZ", "SANTIAGO DE MÉNDEZ"),
        ("ZUMBI", "ZUMBI"),
        ("PUERTO EL CARMEN DE PUTUMAYO", "PUERTO EL CARMEN DE PUTUMAYO"),
        ("PATATE", "PATATE"),
        ("OLMEDO", "OLMEDO"),
        ("PUERTO VILLAMIL", "PUERTO VILLAMIL"),
        ("EL DORADO DE CASCALES", "EL DORADO DE CASCALES"),
        ("LUMBAQUI", "LUMBAQUI"),
        ("PALANDA", "PALANDA"),
        ("SIGCHOS", "SIGCHOS"),
        ("PINDAL", "PINDAL"),
        ("GUAYZIMI", "GUAYZIMI"),
        ("BAEZA", "BAEZA"),
        ("EL CORAZÓN", "EL CORAZÓN"),
        ("PACCHA", "PACCHA"),
        ("AMALUZA", "AMALUZA"),
        ("LAS NAVES", "LAS NAVES"),
        ("LOGROÑO", "LOGROÑO"),
        ("SAN FERNANDO", "SAN FERNANDO"),
        ("GONZANAMÁ", "GONZANAMÁ"),
        ("SAN JUAN BOSCO", "SAN JUAN BOSCO"),
        ("YACUAMBI", "YACUAMBI"),
        ("SANTA CLARA", "SANTA CLARA"),
        ("ARAJUNO", "ARAJUNO"),
        ("TARAPOA", "TARAPOA"),
        ("TISALEO", "TISALEO"),
        ("SUSCAL", "SUSCAL"),
        ("NABÓN", "NABÓN"),
        ("MOCHA", "MOCHA"),
        ("LA VICTORIA", "LA VICTORIA"),
        ("GUACHAPALA", "GUACHAPALA"),
        ("SANTIAGO", "SANTIAGO"),
        ("CHAGUARPAMBA", "CHAGUARPAMBA"),
        ("PENIPE", "PENIPE"),
        ("TAISHA", "TAISHA"),
        ("CHILLA", "CHILLA"),
        ("PAQUISHA", "PAQUISHA"),
        ("CARLOS JULIO AROSEMENA TOLA", "CARLOS JULIO AROSEMENA TOLA"),
        ("SOZORANGA", "SOZORANGA"),
        ("PUCARÁ", "PUCARÁ"),
        ("HUAMBOYA", "HUAMBOYA"),
        ("QUILANGA", "QUILANGA"),
        ("OÑA", "OÑA"),
        ("SEVILLA DE ORO", "SEVILLA DE ORO"),
        ("MERA", "MERA"),
        ("PABLO SEXTO", "PABLO SEXTO"),
        ("OLMEDO", "OLMEDO"),
        ("DÉLEG", "DÉLEG"),
        ("LA BONITA", "LA BONITA"),
        ("EL PAN", "EL PAN"),
        ("TIPUTINI", "TIPUTINI"),
        ("BUCAY", "BUCAY"),
        ("LA MANA", "LA MANA"),
        ("LOS ANDES", "LOS ANDES"),
        ("SALCEDO", "SALCEDO"),
        (
            "EL COCA (Puerto Francisco de Orellana)",
            "EL COCA (Puerto Francisco de Orellana)",
        ),
        ("SIGSIG", "SIGSIG"),
        ("QUININDE", "QUININDE"),
    ]

    SUPERVISOR_RANGE = [
        ("ALL", "ALL"),
        ("GUSTAVO", "GUSTAVO"),
        ("NICOLE", "NICOLE"),
        ("SIDNWEY", "SIDNWEY"),
        ("JOHANA", "JOHANA"),
    ]

    RESPONSE_STATUS_TYPE = [
        ("0", "ALL"),
        ("1", "No Contactado"),
        ("2", "Contactado - no vendido"),
        ("3", "Contactado - vendido"),
    ]


    response_status = forms.ChoiceField(
        required=True,
        choices=RESPONSE_STATUS_TYPE,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "filter-respStatus",
            },
        ),
    )

    dateFrom = forms.DateField(
        #input_formats = ["%Y-%m-%d"],
        required=False,
        widget=forms.DateInput(
            #format=["%Y-%m-%d"],
            attrs={
                "class": "form-control",
                "id": "filter-date-from",
                "placeholder": "Selecciona una fecha",
                "type": "date",
            },
        ),
    )

    dateTo = forms.DateField(
        #input_formats = ["%Y-%m-%d"],
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "id": "filter-date-to",
                "placeholder": "Selecciona una fecha",
                "type": "date",
            },
        ),
    )

    BIRTH_MONTH_CHOICES = [
        ("ALL", "ALL"),
        ("01", "Enero"),
        ("02", "Febrero"),
        ("03", "Marzo"),
        ("04", "Abril"),
        ("05", "Mayo"),
        ("06", "Junio"),
        ("07", "Julio"),
        ("08", "Agosto"),
        ("09", "Septiembre"),
        ("10", "Octubre"),
        ("11", "Noviembre"),
        ("12", "Diciembre"),
    ]

    birthMonth = forms.MultipleChoiceField(
        required=False,
        choices=BIRTH_MONTH_CHOICES,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-control",
                "id": "filter-birthMonth",
            },
        ),
    )

    edadFrom = forms.ChoiceField(
        required=False,
        choices=OLD_RANGE,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "filter-edad-from",
            },
        ),
    )

    edadTo = forms.ChoiceField(
        required=False,
        choices=OLD_RANGE[::-1],
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "filter-edad-to",
            },
        ),
    )

    CUPO_RANGE = [
        (0, 0),  (50, 50),
        (100, 100),  (150, 150),
        (200, 200), (250, 250),
        (300, 300), (350, 350),
        (400, 400), (500, 500),
        (600, 600), (700, 700),
        (800, 800), (900, 900),
        (1000, 1000), (1250, 1250),
        (1500, 1500), (1750, 1750),
        (2000, 2000), (2500, 2500) 
    ]

    cupoFrom = forms.ChoiceField(
        required=False,
        choices=CUPO_RANGE,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "filter-cupo-from",
            },
        ),
    )

    cupoTo = forms.ChoiceField(
        required=False,
        choices=CUPO_RANGE[::-1],
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "filter-cupo-to",
            },
        ),
    )


    ventaFrom = forms.ChoiceField(
        required=False,
        choices=VENTA_RANGE,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "filter-venta-from",
            },
        ),
    )
    ventaTo = forms.ChoiceField(
        required=False,
        choices=VENTA_RANGE[::-1],
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "filter-venta-to",
            },
        ),
    )

    

    ciudad = forms.MultipleChoiceField(
        required=True,
        choices=CIUDAD_RANGE,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-control",
                "id": "filter-ciudad",
            },
        ),
    )

    TYPE_SEXO = [
        ("ALL", "ALL"),
        ("MASCULINO", "HOMBRES"),
        ("FEMENINO", "MUJERES"),
    ]

    sexo = forms.ChoiceField(
        required=True,
        choices=TYPE_SEXO,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "filter-sexo",
            },
        ),
    )

    socio_pycca = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
                "id": "filter-socioPycca",
            },
        ),
    )

    frecuenciaVenta = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
                "id": "filter-frecuenciaVenta",
            },
        ),
    )

    FRECUENCIA_RANGE = [
        (0, 0), 
        (1, 1), 
        (2, 2), 
        (3, 3), 
        (4, 4), 
        (6, 6), 
        (8, 8), 
        (9, 9),
        (10, 10), (15, 15),
        (20, 20), (25, 25) 
    ]

    frecuenciaFrom = forms.ChoiceField(
        required=False,
        choices=FRECUENCIA_RANGE,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "filter-frecuencia-from",
            },
        ),
    )

    frecuenciaTo = forms.ChoiceField(
        required=False,
        choices=FRECUENCIA_RANGE[::-1],
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "filter-frecuencia-to",
            },
        ),
    )
    

    activate_edad = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input border border-white',
        'id': 'flexSwitchCheckDefault'
    }))
  
    def __init__(self, *args, **kwargs):
        initial_values = kwargs.pop("initial_values", None)
        super(create_filter_form, self).__init__(*args, **kwargs)

        if initial_values:
            self.initial.update(initial_values)
        else:
            self.fields['ciudad'].initial = ['ALL']
            self.fields['birthMonth'].initial = ['ALL']
            #self.fields['activate_edad'].initial = False

