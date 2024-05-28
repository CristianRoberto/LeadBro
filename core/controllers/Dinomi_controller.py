import csv
from django.http import BadHeaderError, HttpRequest, HttpResponse
from ..AWS.RDS import connection
from ..forms.create_dinomi_form import create_dinomi_form
from django.shortcuts import render, redirect
from mysql.connector import IntegrityError
from datetime import datetime
import json

template_name = "Dinomi.html"


def __get_data():
    query = "SELECT * " "FROM post_requests  ORDER BY id DESC" 

    with connection() as conn:
        conn.execute(query)
        result = conn.fetchall()

        if result:
            return result
        return None

def __insert_new_dinomi_data(data):
    form = create_dinomi_form(data)

    if form.is_valid():
        data = (
            form.cleaned_data["startDate"],
            form.cleaned_data["endDate"],
            form.cleaned_data["tipo"],
            form.cleaned_data["nombre_dinomi"].upper(),
            "activo",
            form.cleaned_data["equipo_dinomi"].upper(),            
        )
        atributos = {}
        for i in range(1,6):
            clave = form.cleaned_data.get(f"atributo_tipo_{i}")
            valor = form.cleaned_data.get(f"atributo_nombre_{i}")            
            if clave and valor:  # Asegurar que ambos, clave y valor, estén presentes
                if clave in atributos:
                    return False
                
                atributos[clave] = valor
        
        atributos_json = json.dumps(atributos)

        # Agrega `atributos_json` a tus datos para la inserción
        data += (atributos_json,)

        query = (
            "INSERT INTO post_requests (fecha_ini, fecha_fin, tipo, campania, estado, equipo, atributos)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )

        success = False

        with connection() as conn:
            conn.execute(query, data)
            if conn.rowcount == 1:
                success = True
            id_request = conn.lastrowid
            conn.close()

        return success


# TODO: configurar los parametros del form para la data
def __zip_data_and_forms(data):
        
    filter_to_edit = (
        [
            create_dinomi_form(
                initial_values={
                    "startDate": line[1].strftime("%Y-%m-%d"),
                    "endDate":line[2].strftime("%Y-%m-%d"),
                    "tipo": line[3],
                    "nombre_dinomi": line[4],
                    "estado_dinomi": line[5],
                    "equipo_dinomi": line[6],
                    "id": line[0],
                }
            )
            for line in data
        ]
        if data
        else []
    )

    dinomi_info = zip(data, filter_to_edit)

    return dinomi_info


def __checkRequirements(req):
    if req.method == "POST":
        body = req.POST
        if "new_dinomi_insert" in body:
            result = __insert_new_dinomi_data(body)

            context = __set_context()
            context.update({"insert_state": "sucess" if result else "fail", "message": "Registro exitoso" if result else "Fallo en el registro"})
            return context

        if "vista_crear" in body:
            context = __set_context()
            context.update({"activarRegistro": True})
            return context
        
        if "vista_registro" in body:
            context = __set_context()
            return context
        return
    


def __set_context():

    data = __get_data()

    context = {
        "dinomi_table_info": __zip_data_and_forms(data),
        "dinomi_form": create_dinomi_form,
    }

    return context


def process_dinomi_page(req):
    context = __checkRequirements(req)

    if not context:
        context = __set_context()

    return render(req, template_name, context)
