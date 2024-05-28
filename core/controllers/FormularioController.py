import ast
import csv
import json
import requests
from django.http import Http404, HttpResponse, JsonResponse
from ..AWS.RDS import connection
from ..forms.create_form_leads import create_form_pycca, create_form_laica, create_form_cnt, create_form_zurich
from datetime import datetime

from django.shortcuts import render, redirect
from mysql.connector import IntegrityError
from django.core.paginator import Paginator

template_name = "formularios.html"
splitPages = 20
leads_table = "leads2"
operador_table = "operador2"
historialOperador_table = "historial_operador2"
cliente_table = "clientes2"
celular_table = "celular_cliente2"
telefono_table = "telefono_cliente2"
correo_table = "correo_cliente2"

def __getProducto(compania):
    query = (
        "SELECT p.id, subcp.nombre,"
        "    p.nombre "
        "FROM producto p "
        "JOIN subcategoriaProducto subcp ON p.id_subcategoria = subcp.id "
        "JOIN categoriaProducto cp ON cp.id = subcp.id_categoria "
        "JOIN compania comp ON comp.id = cp.id_compania "
        "WHERE comp.nombre = %s "
    )

    with connection() as conn:
        conn.execute(query, (compania,))
        productos = conn.fetchall()

    listProductos = []
    if len(productos) > 0:
        for producto in productos:
            #listProductos.append((producto[0], f"{producto[1]} - {producto[2]}"))
            listProductos.append((producto[0], f"{producto[2]}"))
    return listProductos

def __getSubcampanas(campana):
    query = (
        "SELECT subcamp.id, "
        "    subcamp.nombre "
        "FROM subcampana subcamp "
        "JOIN campana camp ON camp.id = subcamp.id_campana "
        "WHERE camp.id = %s "
    )

    with connection() as conn:
        conn.execute(query, (campana,))
        subcampanas = conn.fetchall()

    return subcampanas if subcampanas else []


def __getOperadorData(username):
    query = (
        "SELECT * "
        f"FROM {operador_table} "
        "WHERE usuario = %s "
    )

    with connection() as conn:
        conn.execute(query, (username,))
        operador = conn.fetchone()
    
    return operador

def __getOperadores():
    query = (
        "SELECT id, nombreCompleto "
        f"FROM {operador_table} "        
    )

    with connection() as conn:
        conn.execute(query)
        result = [i for i in conn]
    
    return result

def __ValidarCLiente(cliente_data):
    query_verifica_cliente = f"SELECT * FROM {cliente_table}  WHERE cedula = %s LIMIT 1"
    query_insert_cliente = (
        f"INSERT INTO {cliente_table}  (cedula, nombres, apellidos) VALUES ( %s, %s, %s) "
    )

    query_verifica_celular = (
        f"SELECT * FROM {celular_table} WHERE celular = %s and id_cliente = %s LIMIT 1"
    )
    query_insert_celular = (
        f"INSERT INTO {celular_table}  (celular, id_cliente) VALUES ( %s, %s) "
    )

    query_verifica_telefono = f"SELECT * FROM {telefono_table} WHERE telefono = %s and id_cliente = %s LIMIT 1"
    query_insert_telefono = (
        f"INSERT INTO {telefono_table}  (telefono, id_cliente) VALUES ( %s, %s) "
    )

    query_verifica_correo = (
        f"SELECT * FROM {correo_table} WHERE correo = %s and id_cliente = %s LIMIT 1"
    )
    query_insert_correo = (
        f"INSERT INTO {correo_table}  (correo, id_cliente) VALUES ( %s, %s) "
    )

    id_cliente = None
    id_celular = None
    id_correo = None
    id_telefono = None

    with connection() as conn:
        conn.execute(query_verifica_cliente, (cliente_data["cedula_value"],))
        cliente = conn.fetchall()
    if cliente:
        id_cliente = cliente[0][0]

        # ********** Consulta celular ******************
        with connection() as conn:
            conn.execute(
                query_verifica_celular, (cliente_data["celular_value"], id_cliente)
            )
            celular = conn.fetchall()
        if celular:
            id_celular = celular[0][0]
        else:
            with connection() as conn:
                conn.execute(
                    query_insert_celular, (cliente_data["celular_value"], id_cliente)
                )
                if conn.rowcount == 1:
                    id_celular = conn.lastrowid
                conn.close()

        # ********** Consulta correo ******************
        if cliente_data["correo_value"]:
            with connection() as conn:
                conn.execute(
                    query_verifica_correo, (cliente_data["correo_value"], id_cliente)
                )
                correo = conn.fetchall()

            if correo:
                id_correo = correo[0][0]
            else:
                with connection() as conn:
                    conn.execute(
                        query_insert_correo, (cliente_data["correo_value"], id_cliente)
                    )
                    if conn.rowcount == 1:
                        id_correo = conn.lastrowid
                    conn.close()

        # ********** Consulta telefono ******************
        if cliente_data["telefono_value"]:
            with connection() as conn:
                conn.execute(
                    query_verifica_telefono,
                    (cliente_data["telefono_value"], id_cliente),
                )
                telefono = conn.fetchall()

            if telefono:
                id_telefono = telefono[0][0]
            else:
                with connection() as conn:
                    conn.execute(
                        query_insert_telefono,
                        (cliente_data["telefono_value"], id_cliente),
                    )
                    if conn.rowcount == 1:
                        id_telefono = conn.lastrowid
                    conn.close()

    else:
        # ******** registrar cliente **************
        with connection() as conn:
            conn.execute(
                query_insert_cliente,
                (
                    cliente_data["cedula_value"],
                    cliente_data["nombre_value"],
                    cliente_data["apellido_value"],
                ),
            )
            if conn.rowcount == 1:
                id_cliente = conn.lastrowid
            conn.close()

        # ******** celular cliente **************
        with connection() as conn:
            conn.execute(
                query_insert_celular, (cliente_data["celular_value"], id_cliente)
            )
            if conn.rowcount == 1:
                id_celular = conn.lastrowid
            conn.close()

        # ******** correo cliente **************
        if cliente_data["correo_value"]:
            with connection() as conn:
                conn.execute(
                    query_insert_correo, (cliente_data["correo_value"], id_cliente)
                )
                if conn.rowcount == 1:
                    id_correo = conn.lastrowid
                conn.close()

        # ******** telefono cliente **************
        if cliente_data["telefono_value"]:
            with connection() as conn:
                conn.execute(
                    query_insert_telefono, (cliente_data["telefono_value"], id_cliente)
                )
                if conn.rowcount == 1:
                    id_telefono = conn.lastrowid
                conn.close()

    return (id_cliente, id_celular, id_correo, id_telefono)


def __validarOperador(nombre):
    query_verifica_operador = (
        "SELECT * FROM operador  WHERE nombreCompleto = %s LIMIT 1"
    )
    id_operador = None
    with connection() as conn:
        conn.execute(query_verifica_operador, (nombre,))
        operador = conn.fetchall()

    if operador:
        id_operador = operador[0][0]

    return id_operador

def __gestion_leadPycca(form: create_form_pycca, segmentada = False):
    cliente_data = {
        "nombre_value": form.cleaned_data["nombre"],
        "apellido_value": form.cleaned_data["apellido"],
        "cedula_value": form.cleaned_data["cedula"],
        "celular_value": form.cleaned_data["celular"],
        "correo_value": form.cleaned_data["correo"],
        "telefono_value": form.cleaned_data["telefono"],
    }
    
    id_operador = form.cleaned_data["operador"]

    valor = (
        int(form.cleaned_data["valor_facturado_entero"])
        + int(form.cleaned_data["valor_facturado_decimal"]) / 100
    )
    valor_sin_iva = valor/(int(form.cleaned_data["Iva"] ) * 0.01 +1) 

    id_campana = form.cleaned_data["campana"]
    id_subcampana = form.cleaned_data["subcampana"]
    id_producto = form.cleaned_data["producto"]

    lead_pycca_data = {
        "id_campana": id_campana,
        "id_subcampana": id_subcampana,
        "ciudad": form.cleaned_data["ciudad"],
        "marca_temporal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "id_producto": id_producto,
        "descripcion_producto": form.cleaned_data["descripcion"],
        "valor": str(valor),
        "valor_sin_iva": f"{valor_sin_iva:.2f}",
        "tipo_venta": form.cleaned_data["tipo_venta"],
        "acepta_seguro": form.cleaned_data["acepta_seguro"],
    }   

    # Verificar y Obtener el id del cliente
    
    id_cliente, id_celular, id_correo, id_telefono = __ValidarCLiente(cliente_data)

    listProductos = __getProducto("PYCCA")
    dict_Productos = dict(listProductos)

    listOperadores = __getOperadores()
    dict_operadores = dict(listOperadores)

    listSubcampanas = __getSubcampanas(id_campana)
    dict_Subcampanas = dict(listSubcampanas)

    if not id_cliente:
        context = {
            "data_form_leads": create_form_pycca(list_productos=listProductos, list_operador = [(id_operador, dict_operadores.get(id_operador))] if segmentada else listOperadores),
            "form_leads_id": "Pycca",
            "lead_error_message": "Error: Problemas con el servidor al registrar el cliente."          
        }
        return context

    lead_pycca_data["id_cliente"] = id_cliente
    lead_pycca_data["id_celular"] = id_celular
    lead_pycca_data["id_operador"] = id_operador

    if id_telefono:
        lead_pycca_data["id_telefono"] = id_telefono

    if id_correo:
        lead_pycca_data["id_correo"] = id_correo


    result = __insertarLeads(lead_pycca_data)

    sheetdata = {}
    sheetdata.update(cliente_data)
    sheetdata["operador_name"] = dict_operadores.get(int(id_operador))
    sheetdata.update(lead_pycca_data)
    sheetdata["subcampana"] = dict_Subcampanas.get(int(id_subcampana))
    sheetdata["producto"] = dict_Productos.get(int(id_producto))
    print(sheetdata)
    result_upload = True#__upload2GoogleSheet(sheetdata, "PYCCA")

    context = {
        "data_form_leads": create_form_pycca(list_productos=listProductos, list_operador = [(id_operador, dict_operadores.get(id_operador))] if segmentada else listOperadores),
        "form_leads_id": "PYCCA",
    }
    if result and result_upload:
        context.update({"lead_success_message": "Lead de Pycca registrado."})
    elif not result_upload:
        context.update({"lead_error_message": "Error: Problemas al registrar lead en Produccion."})
    else:
        context.update({"lead_error_message": "Error: Problemas en el servidor para registrar lead."})
    return context

def __gestion_leadLaica (form: create_form_laica, segmentada = False):
    cliente_data = {
        "nombre_value": form.cleaned_data["nombre"],
        "apellido_value": form.cleaned_data["apellido"],
        "cedula_value": form.cleaned_data["cedula"],
        "celular_value": form.cleaned_data["celular"],
        "correo_value": form.cleaned_data["correo"],
        "telefono_value": form.cleaned_data["telefono"],
    }

    id_operador = form.cleaned_data["operador"],

    valor = (
        int(form.cleaned_data["valor_facturado_entero"])
        + int(form.cleaned_data["valor_facturado_decimal"]) / 100
    )
    
    #valor_iva = valor*(int(form.cleaned_data["Iva"] ) * 0.01 +1)

    lead_laica_data = {
        "id_campana": form.cleaned_data["campana"],
        "id_subcampana": form.cleaned_data["subcampana"],
        "marca_temporal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "id_producto": 569,
        "valor_sin_iva": str(valor),
        "descripcion_producto": form.cleaned_data["facultad"] + "-" + form.cleaned_data["carrera"] + "-" + form.cleaned_data["modalidad"],
        #"valor": f"{valor_iva:.2f}",
    }   

    # Verificar y Obtener el id del cliente
    id_cliente, id_celular, id_correo, id_telefono = __ValidarCLiente(cliente_data)

    listOperadores = __getOperadores()
    dict_operadores = dict(listOperadores)

    listSubcampanas = __getSubcampanas(lead_laica_data("id_campana"))
    dict_Subcampanas = dict(listSubcampanas)

    if not id_cliente:
        context = {
            "data_form_leads": create_form_laica(list_operador = [(id_operador, dict_operadores.get(id_operador))] if segmentada else listOperadores),
            "form_leads_id": "Laica",
            "lead_error_message": "Error: Problemas con el servidor al registrar el cliente."          
        }
        return context
        
    lead_laica_data["id_cliente"] = id_cliente
    lead_laica_data["id_celular"] = id_celular
    lead_laica_data["id_operador"] = id_operador


    if id_telefono:
        lead_laica_data["id_telefono"] = id_telefono

    if id_correo:
        lead_laica_data["id_correo"] = id_correo

    if form.cleaned_data["fecha_1stContact"]:
        lead_laica_data["fecha_1stContact"] = form.cleaned_data["fecha_1stContact"].strftime('%Y-%m-%d')

    result = __insertarLeads(lead_laica_data)

    sheetdata = {}
    sheetdata.update(cliente_data)
    sheetdata["operador_name"] = dict_operadores.get(int(id_operador))
    sheetdata.update(lead_laica_data)
    sheetdata["subcampana"] = dict_Subcampanas.get(int(lead_laica_data("id_subcampana")))
    #result_upload = __upload2GoogleSheet(sheetdata, "Laica")
    result_upload = False

    context = {
        "data_form_leads": create_form_laica(list_operador = [(id_operador, dict_operadores.get(id_operador))] if segmentada else listOperadores),
        "form_leads_id": "Laica"
    }
    if result and result_upload:
        context.update({"lead_success_message": "Lead de Laica registrado."})
    elif not result_upload:
        context.update({"lead_error_message": "Error: Problemas al registrar lead en Produccion."})
    else:
        context.update({"lead_error_message": "Error: Problemas en el servidor para registrar lead."})

    return context

def __insertarLeads(data_lead):
    
    fields = ", ".join(data_lead.keys())
    placeholders = ", ".join(['%s' for _ in data_lead.values()])
    query = f"INSERT INTO {leads_table} ({fields}) VALUES ({placeholders})"
    #values = ", ".join(f"'{str(value)}'" if isinstance(value, str) else str(value) for value in data_lead.values())

    with connection() as conn:
        conn.execute(
            query, tuple(data_lead.values())
        )
        if conn.rowcount == 1:
            id_lead = conn.lastrowid
        conn.close()   
    
    return True if id_lead else False


def __upload2GoogleSheet(data_lead, typeForm):
    data_lead["typeForm"] = typeForm

    url = ""
    if typeForm == "PYCCA":
        #url = "https://hooks.zapier.com/hooks/catch/8982033/3nnt4jd/"  
        url = "https://hooks.zapier.com/hooks/catch/8982033/37qh7p7/"  
    if typeForm == "Laica":
        url = "https://hooks.zapier.com/hooks/catch/8982033/3nnhk9s/" 

    headers = {'Content-Type': 'application/json'}  # Define los encabezados de la solicitud HTTP

    response = requests.post(url, data=json.dumps(data_lead), headers=headers)

    if response.status_code == 200:
        print('Datos enviados exitosamente.')
        return True
    else:
        print(f'Error: {response.status_code}')
        return False


def __validarForm(body, segmentado = False):


    typeForm = body["compania"]


    if typeForm == "PYCCA":
        listProductos = __getProducto("PYCCA")
        list_operadores =  __getOperadores()
        listSubcampanas = __getSubcampanas(body["campana"])

        form = create_form_pycca(data=body, list_productos=listProductos, list_subcampanas= listSubcampanas, list_operador = list_operadores)

        if form.is_valid():
            result = __gestion_leadPycca(form, segmentado)
            return result

        else:
            print(form.errors)
            print("form is not available")
            context = {
                "data_form_leads": form,
                "form_leads_id": "PYCCA",
            }

            return context

    if typeForm == "Laica":
        list_operadores =  __getOperadores()
        form = create_form_laica(body, list_operador = list_operadores)

        if form.is_valid():
            result = __gestion_leadLaica(form)
            return result

        else:
            print(form.errors)
            print("form is not available")
            context = {
                "data_form_leads": form,
                "form_leads_id": "Laica",
            }

            return context

    if typeForm == "Zurich":

        form = create_form_laica(body)

        if form.is_valid():
            result = __gestion_leadLaica(form)
            return result

        else:
            print(form.errors)
            print("form is not available")
            return form


def __checkProfile(req):
    grupos = req.user.groups.all()    
    grupos = [grupo.name for grupo in grupos]

    if "OPERADOR" in grupos:
        query = (
            "SELECT comp.nombre "
            f"FROM {historialOperador_table} hop "
            "JOIN operador op ON op.id = hop.id_operador "
            "JOIN campana cp ON cp.id = hop.id_campana "
            "JOIN compania comp ON comp.id = cp.id_compania "
            "WHERE op.usuario = %s "
                "AND MONTH(hop.fecha) = %s "
                "AND YEAR(hop.fecha) =  %s "
        )

        now = datetime.now()
        current_year = now.year
        current_month = now.month

        with connection() as conn:
            conn.execute(query, (req.user.username,current_month, current_year))
            companias = conn.fetchall()
        
        if len(companias) > 0:
            return [compania[0] for compania in companias]
        else: 
            return ["NINGUNA"]
            
    return 

def __checkRequirements(req):
    if req.method == "POST":
        body = req.POST
        companias = __checkProfile(req)
        operadorData = __getOperadorData(req.user.username)

        if "new_lead_register" in body:
            if companias and not "NINGUNA" in companias and len(companias)>0:
                context = __validarForm(body, segmentado= True)
                context.update({"segmentado": True, "list_lead_forms": companias})

            elif companias and "NINGUNA" in companias:
                context = {
                "error_message":"No tiene ninguna campaña y formulario activado.",
                "segmentado": True,
                }

            else: 
                context = __validarForm(body)

            return context
        
        if companias and "NINGUNA" in companias:
            context = {
                "error_message":"No tiene ninguna campaña y formulario activado.",
            }
            return context
        
        if "lead_form_pycca" in body :

            listProductos = __getProducto("PYCCA")
            context = {
                    "data_form_leads": create_form_pycca(list_productos=listProductos, list_operador = [(operadorData[0], operadorData[5])] if companias and "PYCCA" in companias else __getOperadores()),
                    "form_leads_id": "PYCCA",
                }            
            if companias and "PYCCA" in companias:
                context.update({"segmentado": True, "list_lead_forms": companias})

            return context

        if "lead_form_claro" in body :
            listProductos = __getProducto("PYCCA")
            context = {
                    "data_form_leads": create_form_pycca(list_productos=listProductos, list_operador = [(operadorData[0], operadorData[5])] if companias and "PYCCA" in companias else __getOperadores()),
                    "form_leads_id": "PYCCA",
                }            
            if companias and "PYCCA" in companias:
                context.update({"segmentado": True, "list_lead_forms": companias})

            return context

        if "lead_form_laica":            
            context = {"data_form_leads": create_form_laica(list_operador = [(operadorData[0], operadorData[5])] if companias and "LAICA" in companias else __getOperadores()), "form_leads_id": "Laica"}
            
            if companias and "LAICA" in companias:
                context.update({"segmentado": True, "list_lead_forms": companias})
            return context

        if "lead_form_zurich" in body and ("ZURICH" in companias or not companias):
            listProductos = __getProducto("PYCCA")
            context = {
                    "data_form_leads": create_form_pycca(list_productos=listProductos, list_operador = [(operadorData[0], operadorData[5])] if companias and "PYCCA" in companias else __getOperadores()),
                    "form_leads_id": "PYCCA",
                }            
            if companias and "PYCCA" in companias:
                context.update({"segmentado": True, "list_lead_forms": companias})

            return context

        if "lead_form_cnt" in body and ( "CNT" in companias or not companias):
            listProductos = __getProducto("PYCCA")
            context = {
                    "data_form_leads": create_form_pycca(list_productos=listProductos, list_operador = [(operadorData[0], operadorData[5])] if companias and "PYCCA" in companias else __getOperadores()),
                    "form_leads_id": "PYCCA",
                }            
            if companias and "PYCCA" in companias:
                context.update({"segmentado": True, "list_lead_forms": companias})

            return context
        
        
        
        
    
    if req.method == "GET":
        companias = __checkProfile(req)

        if companias and not "NINGUNA" in companias:
            operadorData = __getOperadorData(req.user.username)
            
            context = {}
            if "PYCCA" in companias:
                listProductos = __getProducto("PYCCA")
                
                context = {
                    "data_form_leads": create_form_pycca(list_productos=listProductos, list_operador =[(operadorData[0], operadorData[5])] ),
                    "form_leads_id": "PYCCA",
                    "segmentado": True
                }

            if "CLARO" in companias:
                if not "form_leads_id" in context:
                    context = {
                        "data_form_leads": create_form_pycca(list_productos=listProductos, list_operador =[(operadorData[0], operadorData[5])] ), #TODO: cambiar
                        "form_leads_id": "Claro",
                        "segmentado": True
                    }

            if "CNT" in companias:
                if not "form_leads_id" in context:
                    context = {
                        "data_form_leads": create_form_pycca(list_productos=listProductos, list_operador =[(operadorData[0], operadorData[5])] ), #TODO: cambiar
                        "form_leads_id": "CNT",
                        "segmentado": True
                    }
            if "ZURICH" in companias:
                if not "form_leads_id" in context:
                    context = {
                        "data_form_leads": create_form_pycca(list_productos=listProductos, list_operador =[(operadorData[0], operadorData[5])] ),  # TODO: cambiar
                        "form_leads_id": "Zurich",
                        "segmentado": True
                    }
            if "LAICA" in companias:
                if not "form_leads_id" in context:
                    context = {
                        "data_form_leads": create_form_laica(list_operador =[(operadorData[0], operadorData[5])]), 
                        "form_leads_id": "Laica",
                        "segmentado": True
                    }

            context.update(
                {"list_lead_forms": companias}
            )
            return context
        elif companias and "NINGUNA" in companias:            
            context = {
                "error_message":"No tiene ninguna campaña y formulario activado.",
                "segmentado": True
            }
            return context
        else:
            return


def __set_context():
    listProductos = __getProducto("PYCCA")
    list_operadores = __getOperadores()

    context = {
        "data_form_leads": create_form_pycca(list_productos=listProductos, list_operador = list_operadores),
        "form_leads_id": "PYCCA",
    }

    return context


def process_formulario_page(req):

    context = __checkRequirements(req)

    if not context:
        context = __set_context()

    return render(req, template_name, context)
