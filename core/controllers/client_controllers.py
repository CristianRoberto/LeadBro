import ast
import csv
import json
import os  # Importa el módulo os para manejar rutas de archivos
from urllib import request
from django.http import HttpResponse, HttpResponseRedirect  # Importa HttpResponseRedirect
from ..AWS.RDS import connection
from ..forms.search_client_form import search_client_form
from ..forms.edit_editarcliente_form import EditClienteForm

from django.shortcuts import render, redirect
from mysql.connector import IntegrityError
from django.core.paginator import Paginator

template_name = "search_client.html"
splitPages = 20


def __search_client_contacts(id_cliente):
    result_contacts = tuple()

    query_celular = (
        "SELECT cel.id, "
        "    cel.celular "
        "FROM celular_cliente cel "
        "WHERE cel.id_cliente = %s"
    )

    query_telef = (
        "SELECT telf.id, "
        "    telf.telefono "
        "FROM telefono_cliente telf "
        "WHERE telf.id_cliente = %s"
    )

    query_correo = (
        "SELECT email.id, "
        "    email.correo "
        "FROM correo_cliente email "
        "WHERE email.id_cliente = %s"
    )

    with connection() as conn:
        conn.execute(query_celular, (id_cliente,))
        result_celulares = conn.fetchall()
        if not result_celulares:
            result_celulares = []
        result_contacts += tuple([result_celulares])

        conn.execute(query_telef, (id_cliente,))
        result_telef = conn.fetchall()
        if not result_telef:
            result_telef = []
        result_contacts += tuple([result_telef])

        conn.execute(query_correo, (id_cliente,))
        result_correo = conn.fetchall()
        if not result_correo:
            result_correo = []
        result_contacts += tuple([result_correo])
    
    return result_contacts


def __new_client_data(data):
    form = search_client_form(data)
    if form.is_valid():
        cedula_value = form.cleaned_data["cedula"]
        celular_value = form.cleaned_data["celular"]

        query = (
            "SELECT l.id, "
            "    l.nombres, "
            "    l.apellidos, "
            "    l.cedula, "
            "    l.fecha_nacimiento, "
            "    l.edad, "
            "    l.genero, "
            "    l.ciudad,"
            "    l.provincia, "
            "    l.estado_civil "
            "FROM cliente l "
        )

        conditions = []
        params = []

        if cedula_value:
            conditions.append("l.cedula = %s")
            params.append(cedula_value)

        if celular_value:
            query += " JOIN celular_cliente cc ON l.id = cc.id_cliente "
            conditions.append("cc.celular = %s")
            params.append(celular_value)

        if not conditions:
            return None  # No se proporcionó ni cédula ni celular

        query += " WHERE " + " OR ".join(conditions)

        with connection() as conn:
            result_cliente = conn.execute(query, params)
            result_cliente = conn.fetchone()

            if result_cliente:
                id_cliente = result_cliente[0]
                result_cliente += __search_client_contacts(id_cliente)
            else:
                result_cliente = None

        return result_cliente
    else:
        print(form.errors)
        return None


def __update_client_data(data):
    # Construir la lista de clientes con todos los campos necesarios
    customers_list = [
        (data.get('cedula'), 'Cédula: ' + data.get('cedula', '')),
        (data.get('nombres'), 'Nombres: ' + data.get('nombres', '')),
        (data.get('apellidos'), 'Apellidos: ' + data.get('apellidos', '')),
        (data.get('fecha_nacimiento'), 'Fecha de Nacimiento: ' + data.get('fecha_nacimiento', '')),
        (data.get('edad'), 'Edad: ' + str(data.get('edad', ''))),
        (data.get('genero'), 'Género: ' + data.get('genero', '')),
        (data.get('ciudad'), 'Ciudad: ' + data.get('ciudad', '')),
        (data.get('id'), 'ID: ' + str(data.get('id', '')))
    ]
    
    print(f"Datos iniciales: {data}")
    print(f"Lista de clientes: {customers_list}")
    
    form = EditClienteForm(data, initial_values={'customers_list': customers_list})
    
    if form.is_valid():
        print("Formulario válido. Datos limpiados:")
        print(form.cleaned_data)
        
        update_query = (
            "UPDATE cliente SET "
            "nombres = %s, "
            "apellidos = %s, "
            "cedula = %s, "
            "fecha_nacimiento = %s, "
            "edad = %s, "
            "genero = %s, "
            "ciudad = %s "
            "WHERE id = %s"
        )
        values = (
            form.cleaned_data['nombres'],
            form.cleaned_data['apellidos'],
            form.cleaned_data['cedula'],
            form.cleaned_data['fecha_nacimiento'],
            form.cleaned_data['edad'],
            form.cleaned_data['genero'],
            form.cleaned_data['ciudad'],
            form.cleaned_data['id']
        )
        
        print(f"Consulta de actualización: {update_query}")
        print(f"Valores para la consulta: {values}")

        query_successful = False
        try:
            with connection() as conn:
                conn.execute(update_query, values)
                if conn.rowcount:
                    query_successful = True
                    print("Actualización exitosa.")
                else:
                    print("No se actualizó ninguna fila.")
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")

        return query_successful
    else:
        print("Errores en el formulario:")
        print(form.errors)
        return False


def __checkRequirements(req):
    if req.method == "POST":
        body = req.POST

        if "new_client_search" in body:
            data = __new_client_data(body)
            context = __set_context()
            print(data)
            if not data:
                msg = "No existe en cliente en la base de datos.\n"
                context.update({"search_err_msg": msg})
            else:
                context.update({"data_client": data})
            return context
        
        if 'update-campaign-data' in body:
            result = __update_client_data(body)
            if result:
                return redirect(os.path.dirname(req.path))
    
    return __set_context()


def __set_context():
    context = {
        "data_client": None,
        "data_form_state": search_client_form,
    }

    return context


def process_search_client_page(req):
    context = __checkRequirements(req)
    if isinstance(context, HttpResponseRedirect):
        return context
    return render(req, template_name, context)
