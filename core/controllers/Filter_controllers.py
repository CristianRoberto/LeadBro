import csv
from django.http import BadHeaderError, HttpRequest, HttpResponse
from ..AWS.RDS import connection
from ..forms.create_filter_form import create_filter_form
from ..forms.create_filterData_form import create_filterData_form
from ..forms.otp_form import otp_form
from ..utils.otp.otp_config import OTP_ACCESS
from ..utils.email.gmail_config import GMAIL
from django.shortcuts import render, redirect
from mysql.connector import IntegrityError
from datetime import datetime

template_name = "dashboard.html"
splitPages = 100


def __get_data():
    query = (
        "SELECT cl.id, "
        "    cl.cedula, "
        "    cl.nombres, "
        "    cl.apellidos, "
        "    cl.fecha_ultima_transaccion_pycca, "
        "    cl.cupo_pycca, "
        "    cl.ciudad, "
        "    resp.campania AS nombre_campana, "
        "    resp.supervisor,    "
        "    resp.datetime_order    "
        "FROM responses resp "
        "JOIN cliente cl ON cl.id = resp.id_cliente "
        "LIMIT 10"
    )

    query_contact = (
        # "SET SESSION group_concat_max_len = 200; "
        "SELECT "
        "    GROUP_CONCAT(DISTINCT cel.celular SEPARATOR ';') as celulares, "
        "    GROUP_CONCAT(DISTINCT telf.telefono SEPARATOR ';') as telefonos, "
        "    GROUP_CONCAT(DISTINCT mail.correo SEPARATOR ';') as correos "
        "FROM cliente cl "
        "LEFT JOIN celular_cliente cel ON cl.id = cel.id_cliente "
        "LEFT JOIN telefono_cliente telf ON cl.id = telf.id_cliente "
        "LEFT JOIN correo_cliente mail ON cl.id = mail.id_cliente "
        "WHERE cl.id = %s "
        "GROUP BY cl.id "
    )

    with connection() as conn:
        conn.execute(query)
        result = conn.fetchall()
        clientes = []
        for cliente in result:
            conn.execute(query_contact, (cliente[0],))
            contact_result = conn.fetchall()
            if not contact_result:
                contact_result.append(tuple("None", "None", "None"))
            clientes.append(cliente + contact_result[0])

    return clientes


def __build_query(data, typeQuery, limit, selection):
    query_cantidad = "SELECT COUNT(*) AS cantidad FROM cliente cl "
    query_data = (
        "SELECT cl.id, "
        "    cl.cedula, "
        "    cl.nombres, "
        "    cl.apellidos, "
        "    cl.fecha_ultima_transaccion_pycca, "
        "    cl.cupo_pycca, "
    )

    values = ()
    query = ""

    if typeQuery == "cantidad":
        query = query_cantidad
    elif typeQuery == "data":
        query = query_data
        if data["frecuenciaVenta_value"]:
            query += ("    cl.ciudad, "
                 "COUNT(*) AS cantidad "      
            "FROM cliente cl ")
        else:
            query += ("    cl.ciudad " 
            "FROM cliente cl ")

    if selection == "0":

        query += "WHERE "

        if data["socioPycca_value"]:
            query += " cl.cupo_pycca > (%s) AND cl.cupo_pycca < (%s) AND "
            values += (data["cupoFrom_value"], data["cupoTo_value"])

    if selection == "1":

        query += (
            "JOIN responses resp ON cl.id = resp.id_cliente "
            "WHERE (resp.status = (%s) OR resp.status = (%s) OR resp.status = (%s)) "
        )
        query += "AND (DATE(resp.datetime_order) BETWEEN %s AND %s) AND "
        values = (
            "Abandoned",
            "Failure",
            "NoAnswer",
            data["dateFrom_value"],
            data["dateTo_value"],
        )

        if data["socioPycca_value"]:
            query += " cl.cupo_pycca > (%s) AND cl.cupo_pycca < (%s) AND "
            values += (data["cupoFrom_value"], data["cupoTo_value"])

    if selection == "2":
        query += (
            "JOIN responses resp ON cl.id = resp.id_cliente "
            "WHERE resp.id_cliente NOT IN ( "
            "    SELECT l.id_cliente "
            "    FROM leads l "
            ") "
            "AND (resp.status = (%s) OR resp.status = (%s)) "
            "AND (DATE(resp.datetime_order) BETWEEN %s AND %s) AND "
        )
        values = ("ShortCall", "Success", data["dateFrom_value"], data["dateTo_value"])

        if data["socioPycca_value"]:
            query += " cl.cupo_pycca > (%s) AND cl.cupo_pycca < (%s) AND "
            values += (data["cupoFrom_value"], data["cupoTo_value"])

    if selection == "3":
        query += "JOIN leads l ON cl.id = l.id_cliente "

        query += "WHERE (DATE(l.marca_temporal) BETWEEN %s AND %s) AND "
        values = (data["dateFrom_value"], data["dateTo_value"])

        # filtro de venta
        query += " ( l.valor >= %s AND l.valor <= %s) AND "
        values += (data["ventaFrom_value"], data["ventaTo_value"])

        if data["socioPycca_value"]:
            query += " cl.cupo_pycca > (%s) AND cl.cupo_pycca < (%s) AND "
            values += (data["cupoFrom_value"], data["cupoTo_value"])

    if len(data["ciudad_value"]) > 0 and "ALL" not in data["ciudad_value"]:
        placeholders = ", ".join(["%s"] * len(data["ciudad_value"]))
        query += f"cl.ciudad IN ({placeholders}) AND "
        values += tuple(data["ciudad_value"])

    if len(data["birthMonth_value"]) > 0 and "ALL" not in data["birthMonth_value"]:
        placeholders = ", ".join(["%s"] * len(data["birthMonth_value"]))
        query += f"(MONTH(cl.fecha_nacimiento) IN ({placeholders})) AND "
        values += tuple(data["birthMonth_value"])

    # filtro de edad
    if data["edadFrom_value"] and data["edadTo_value"]:
        query += " cl.edad >= %s AND cl.edad <= %s AND "
        values += (data["edadFrom_value"], data["edadTo_value"])

    # filtro de sexo
    if data["sexo_value"] and data["sexo_value"] != "ALL":
        query += " cl.genero = (%s) "
        values += (data["sexo_value"],)

    if "WHERE" in query[-6:]:
        query = query[:-6]

    if "AND" in query[-4:]:
        query = query[:-4]

    if selection != "0" and typeQuery == "data":
        query += "GROUP BY cl.id "

        if selection == "3" and data["frecuenciaVenta_value"]:
            query += "HAVING cantidad >= %s AND cantidad <= %s "
            values += (data["frecuenciaFrom_value"], data["frecuenciaTo_value"])

    if typeQuery == "data" and limit:
        query += "LIMIT 20 "

    if typeQuery == "data" and not limit:
        query += "LIMIT 1000 "
    
    print(query)
    print(values)
    return [query, values]


def __new_filter_data(data, view):
    form = create_filter_form(data)
    if form.is_valid():
        respState_value = form.cleaned_data["response_status"]
        data = {
            "dateFrom_value": form.cleaned_data["dateFrom"],
            "dateTo_value": form.cleaned_data["dateTo"],
            "ciudad_value": form.cleaned_data["ciudad"],
            "birthMonth_value": form.cleaned_data["birthMonth"],
            "edadFrom_value": form.cleaned_data["edadFrom"],
            "edadTo_value": form.cleaned_data["edadTo"],
            "ventaFrom_value": form.cleaned_data["ventaFrom"],
            "ventaTo_value": form.cleaned_data["ventaTo"],
            "sexo_value": form.cleaned_data["sexo"],
            "socioPycca_value": form.cleaned_data["socio_pycca"],
            "cupoFrom_value": form.cleaned_data["cupoFrom"],
            "cupoTo_value": form.cleaned_data["cupoTo"],
            "activateEdad_value": form.cleaned_data["activate_edad"],
            "frecuenciaVenta_value": form.cleaned_data["frecuenciaVenta"],
            "frecuenciaFrom_value": form.cleaned_data["frecuenciaFrom"],
            "frecuenciaTo_value": form.cleaned_data["frecuenciaTo"],
        }

        #print(data)

        query_contact = (
            # "SET SESSION group_concat_max_len = 200; "
            "SELECT "
            "    GROUP_CONCAT(DISTINCT cel.celular SEPARATOR ';') as celulares, "
            "    GROUP_CONCAT(DISTINCT telf.telefono SEPARATOR ';') as telefonos, "
            "    GROUP_CONCAT(DISTINCT mail.correo SEPARATOR ';') as correos, "
            "    COUNT(DISTINCT cel.celular) AS celulares_cant, "
            "    COUNT(DISTINCT telf.telefono) AS telefono_cant, "
            "    COUNT(DISTINCT mail.correo) AS correo_cant "
            "FROM cliente cl "
            "LEFT JOIN celular_cliente cel ON cl.id = cel.id_cliente "
            "LEFT JOIN telefono_cliente telf ON cl.id = telf.id_cliente "
            "LEFT JOIN correo_cliente mail ON cl.id = mail.id_cliente "
            "WHERE cl.id = %s "
            "GROUP BY cl.id "
        )
        # datos solo para presentar
        if view:
            query_cant, values_cant = __build_query(
                data, "cantidad", False, respState_value
            )
            query_data, values_data = __build_query(data, "data", True, respState_value)
            query_contact = (
                "SELECT "
                "    SUBSTRING_INDEX(GROUP_CONCAT(DISTINCT cel.celular ORDER BY LENGTH(cel.celular) DESC SEPARATOR ';'), ';', 1) AS celular,"
                "    SUBSTRING_INDEX(GROUP_CONCAT(DISTINCT telf.telefono ORDER BY LENGTH(telf.telefono) DESC SEPARATOR ';'), ';', 1) AS telefono,"
                "    SUBSTRING_INDEX(GROUP_CONCAT(DISTINCT mail.correo ORDER BY LENGTH(mail.correo) DESC SEPARATOR ';'), ';', 1) AS correo "
                "FROM cliente cl "
                "LEFT JOIN celular_cliente cel ON cl.id = cel.id_cliente "
                "LEFT JOIN telefono_cliente telf ON cl.id = telf.id_cliente "
                "LEFT JOIN correo_cliente mail ON cl.id = mail.id_cliente "
                "WHERE cl.id = %s "
                "GROUP BY cl.id"
            )

            with connection() as conn:
                conn.execute(query_cant, values_cant)
                result_cant = conn.fetchall()

                clientes = []
                if result_cant[0][0] > 0:
                    conn.execute(query_data, values_data)
                    result_data = conn.fetchall()

                    for cliente in result_data:
                        conn.execute(query_contact, (cliente[0],))
                        contact_result = conn.fetchall()
                        if not contact_result:
                            contact_result.append(tuple("None", "None", "None"))
                        contacto = contact_result[0]
                        clientes.append(cliente + contact_result[0])

            return clientes, result_cant[0][0], respState_value

        else:
            query_data, values_data = __build_query(
                data, "data", False, respState_value
            )

            max_telefonos = max_celulares = max_correos = 0

            with connection() as conn:
                conn.execute(query_data, values_data)
                result_data = conn.fetchall()

                clientes = []
                if result_data:
                    for cliente in result_data:
                        conn.execute(query_contact, (cliente[0],))
                        contact_result = conn.fetchall()
                        if not contact_result:
                            contact_result.append(tuple("None", "None", "None"))
                        clientes.append(cliente + contact_result[0])
                        max_celulares = max(max_celulares, int(contact_result[0][3]))
                        max_telefonos = max(max_telefonos, int(contact_result[0][4]))
                        max_correos = max(max_correos, int(contact_result[0][5]))

            return (
                clientes,
                respState_value,
                [max_celulares, max_telefonos, max_correos],
            )

    else:
        print(form.errors)
        return __get_data(), "ERROR"


# TODO: configurar los parametros del form para la data
def __zip_data_and_forms(data):
    filter_to_edit = [
        create_filterData_form(
            initial={
                "cedula": line[1],
                "ventaFrom": line[2],
                "ventaTo": line[2],
                "ciudad": line[2],
                "supervisor": line[2],
                "id": line[0],
            }
        )
        for line in data
    ]

    filter_info = zip(data, filter_to_edit)

    return filter_info


def __send_otp_notification(req, type):
    ip_cliente = __obtener_direccion_ip(req)
    type_access = "descargar" if type == "dw" else "ver"
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result, message = __send_email(
        f"El usuario {req.user.username} con IP address {ip_cliente} en el horario de {hora_actual} solicita acceso para {type_access} en la seccion Base de LeadBro!."
    )
    context = __set_context()

    otp_form_name = "otp_form_dw" if type == "dw" else "otp_form_view"
    otp_notice_name = "otp_notice_dw" if type == "dw" else "otp_notice_view"
    req.session[otp_notice_name] = result

    if result:
        success_message_name = (
            "success_send_message_dw" if type == "dw" else "success_send_message_view"
        )

        context.update(
            {
                otp_form_name: otp_form,
                otp_notice_name: result,
                success_message_name: message,
            }
        )

    else:
        error_send_message_name = (
            "error_send_message_dw" if type == "dw" else "error_send_message_view"
        )

        context.update({otp_notice_name: result, error_send_message_name: message})

    if type == "dw":
        context.update(
            {
                "otp_access_view": req.session["otp_access_view"],
            }
        )
    return context


def __validate_otp(req, data, type):

    form = otp_form(data)
    if form.is_valid():
        otp_code = form.cleaned_data["otp_code"]

        otp_access_name = "otp_access_dw" if type == "dw" else "otp_access_view"
        otp_notice_name = "otp_notice_dw" if type == "dw" else "otp_notice_view"

        otp_access = OTP_ACCESS()

        result = otp_access.verificate_code(otp_code)

        context = __set_context()
        if result:
            req.session[otp_access_name] = result
            context.update(
                {
                    otp_notice_name: True,
                    otp_access_name: result,
                }
            )
            if type == "dw":
                context.update(
                    {
                        "valid_download": True,
                    }
                )
        else:
            otp_form_name = "otp_form_dw" if type == "dw" else "otp_form_view"
            error_validate_message_name = (
                "error_validate_message_dw"
                if type == "dw"
                else "error_validate_message_view"
            )
            msg = "Codigo OTP no válido.\n"
            ip_cliente = __obtener_direccion_ip(req)
            type_access = "descargar" if type == "dw" else "ver"
            hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result, message = __send_email(
                f"El usuario {req.user.username} con IP address {ip_cliente} realizo un intento fallido en el horario de {hora_actual} para {type_access} en la seccion Base de LeadBro!."
            )
            context.update(
                {
                    otp_notice_name: True,
                    error_validate_message_name: msg,
                    otp_form_name: otp_form,
                }
            )

        if type == "dw":
            context.update(
                {
                    "otp_access_view": req.session["otp_access_view"],
                }
            )

        return context
    else:
        return __set_context()


def __obtener_direccion_ip(request: HttpRequest) -> str:
    # Intenta obtener la dirección IP del cliente desde la solicitud HTTP
    direccion_ip = request.META.get("HTTP_X_FORWARDED_FOR", None)

    # Si la dirección IP no está presente en la cabecera 'HTTP_X_FORWARDED_FOR',
    # intenta obtenerla de la cabecera 'REMOTE_ADDR'
    if direccion_ip:
        # En caso de que haya múltiples IPs, toma la primera (la del cliente)
        direccion_ip = direccion_ip.split(",")[0].strip()
    else:
        # Si no hay cabecera 'HTTP_X_FORWARDED_FOR', usa 'REMOTE_ADDR'
        direccion_ip = request.META.get("REMOTE_ADDR", "")

    return direccion_ip


def __send_email(mensaje):

    # email_instance = EMAIL()
    email_instance = GMAIL()

    # send_state, send_message = email_instance.send_message(mensaje)
    send_state, send_log = email_instance.sendMessage(mensaje)

    if send_state:
        return True, "Correo de alerta enviado al administrador exitosamente."
    else:
        return False, send_log


def __processDownload(data, status_table, max_values):

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        'attachment; filename="datos_filtrados.csv"'  # Nombre del archivo que se descargará
    )

    writer = csv.writer(response)
    # Escribir los datos en el archivo CSV

    max_celulares, max_telefonos, max_correos = max_values

    header = [
        "id",
        "cedula",
        "nombres_cliente",
        "apellidos_cliente",
        "fecha_ultima_transaccion_pycca",
        "cupo_pycca",
        "ciudad",
    ]

    # Extender los encabezados con columnas dinámicas
    header.extend([f"celular_{i+1}" for i in range(max_celulares)])
    header.extend([f"telefono_{i+1}" for i in range(max_telefonos)])
    header.extend([f"correo_{i+1}" for i in range(max_correos)])

    writer.writerow(header)
    for item in data:
        row = [
            item[0],
            item[1],
            item[2],
            item[3],
            item[4],
            item[5],
            item[6],
        ]

        celulares = str(item[7]).split(";")
        telefonos = str(item[8]).split(";")
        correos = str(item[9]).split(";")

        # Añadir telefonos, celulares, y correos a la fila
        row.extend(
            celulares + [""] * (max_celulares - len(celulares))
        )  # Rellenar con espacios vacíos si es necesario
        row.extend(
            telefonos + [""] * (max_telefonos - len(telefonos))
        )  # Rellenar con espacios vacíos si es necesario
        row.extend(
            correos + [""] * (max_correos - len(correos))
        )  # Rellenar con espacios vacíos si es necesario
        writer.writerow(row)

    return response


def __checkRequirements(req):
    if req.method == "POST":
        body = req.POST

        if "new_filter_data" in body:

            new_body = body.copy()
            result, cantidad, status_table = __new_filter_data(body, True)

            new_body.pop("csrfmiddlewaretoken")
            new_body["ciudad"] = [new_body["ciudad"]]
            new_body["birthMonth"] = [new_body["birthMonth"]]
            if "activate_edad" in new_body:
                new_body["activate_edad"] = "on"

            req.session["filter_form_memory"] = new_body

            context = {
                "filter": result,
                "filter_cant": int(cantidad),
                "type_table": status_table,
                "filter_form_state": create_filter_form(initial_values=body),
                "filter_data_info": __zip_data_and_forms(result),
                "otp_access_view": req.session["otp_access_view"],
            }
            if "frecuenciaVenta" in new_body:
                context.update(
                    {"frecuenciaVentas": new_body["frecuenciaVenta"],}
                )
                
            return context

        if "download_data_filtered" in body:

            if "filter_form_memory" not in req.session:
                return

            form_memory = req.session["filter_form_memory"]
            # print(form_memory)
            data, status_table, max_values = __new_filter_data(form_memory, False)

            response = __processDownload(data, status_table, max_values)

            req.session["otp_notice_dw"] = False
            req.session["otp_access_dw"] = False

            return response

        if "send-otp-access" in body:
            return __send_otp_notification(req, "ver")

        if "verify-otp-access" in body:

            return (
                __validate_otp(req, body, "view")
                if req.session["otp_notice_view"]
                else __set_context()
            )

        if "send-otp-dw-access" in body:
            return __send_otp_notification(req, "dw")

        if "verify-otp-dw-access" in body:
            return (
                __validate_otp(req, body, "dw")
                if req.session["otp_notice_dw"]
                else __set_context()
            )


def __set_context():

    context = {
        "filter": None,
        "type_table": "0",
        "filter_form_state": create_filter_form,
        "otp_access": False,
        "otp_notice": False,
    }

    return context


def process_filter_page(req):
    context = __checkRequirements(req)
    if isinstance(context, HttpResponse):
        return context

    if not context:
        session_names = [
            "otp_access_view",
            "otp_access_dw",
            "otp_notice_view",
            "otp_notice_dw",
        ]
        req.session.update({name: False for name in session_names})

        context = __set_context()

    return render(req, template_name, context)
