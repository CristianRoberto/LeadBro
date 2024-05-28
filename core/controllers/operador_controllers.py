from django.http import Http404, HttpResponse, HttpResponseRedirect
from ..AWS.RDS import connection
from ..forms.create_operador_form import create_operador_form, edit_operador_form, base_operador_form
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from mysql.connector import IntegrityError
from datetime import datetime

template_name = "operadores.html"
template_edit = "edit_operador.html"

operador_table = "operador2"
lideres_table = "lider"
compania_table = "compania"
historialOperador_table = "historial_operador2"

def __get_operadores():
    query = (
        f"SELECT op.*, ld.nombres FROM {operador_table} op "
        "JOIN lider ld ON ld.id = op.id_lider"
    )
    with connection() as conn:
        conn.execute(query)
        result = [i for i in conn]
    return result


def __get_compania():
    query = (
        f"SELECT id, nombre FROM {compania_table} "
    )
    with connection() as conn:
        conn.execute(query)
        result = [i for i in conn]
    return result

def __getCampanas(compania_id):
    query = (
        "SELECT camp.id, "
        "    camp.nombre "
        "FROM campana camp "
        "JOIN compania com ON com.id = camp.id_compania "
        "WHERE camp.id_compania = %s "
    )

    with connection() as conn:
        conn.execute(query, (compania_id,))
        campanas = conn.fetchall()

    return campanas

# estado = false filtra todos los estados (activo y no activo)
def __get_historial_operador(id_operador, estado=True):
    estado = "AND estado = 1" if estado else " "
    query = (
        f"SELECT hop.*, camp.nombre FROM {historialOperador_table} hop "
        "JOIN campana camp ON camp.id =  hop.id_campana "
        "WHERE id_operador = %s "
        f"{estado} "
            "AND MONTH(fecha) = %s "
            "AND YEAR(fecha) =  %s "
    )

    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    with connection() as conn:
        conn.execute(query, (id_operador, current_month, current_year ))        
        result = [i for i in conn]
    return result


def __get_lideres():
    query = (
        f"SELECT id, nombreCompleto FROM {lideres_table} "
    )
    with connection() as conn:
        conn.execute(query)
        result = [i for i in conn]
    return result


def __get_operador_info(id):
    query = f"SELECT * FROM {operador_table} WHERE id = %s "
    with connection() as conn:
        conn.execute(query, (id,))
        result = conn.fetchone()

    list_lideres = __get_lideres()

    operador_form = base_operador_form(
        initial={
            "cedula": result[1],
            "nombres": result[2],
            "apellidos": result[3],
            "codigoDinomi": result[4],
            "lideres": result[7],
            "id": result[0],
        },
        list_lideres = list_lideres
    )

    list_companias = __get_compania()
    list_historial = __get_historial_operador(id)
    listId_campanas = [historial[2] for historial in list_historial]
    formData = {            
            "compania": list_companias[0][0],
            "id": result[0], #id_operador
        }
    
    if len(list_historial) > 0:
        for record in list_historial:
            formData[f"historialId{record[2]}"] = record[2] #id_campana
            formData[f"historialCampana{record[2]}"] = record[8]
            formData[f"historialCuota{record[2]}"] = record[7]
            formData[f"historialFecha{record[2]}"] = record[3].strftime('%Y-%m-%d')

    historialOperador_form = edit_operador_form(
        initial= formData,
        list_companias = list_companias,
        list_historial_newRegister = listId_campanas,
    )

    return operador_form, historialOperador_form, listId_campanas


def __create_new_operador(data):
    list_lideres = __get_lideres()
    form = create_operador_form(data, list_lideres= list_lideres)
    if form.is_valid():
        cedula = str(form.cleaned_data["cedula"]).zfill(10)
        verify_operador = f"SELECT * FROM {operador_table} " "where cedula = %s "
        existe = False
        with connection() as conn:
            conn.execute(verify_operador, (cedula,))
            result = conn.fetchone()
            if result:
                existe = True
            conn.close()

        add_operador = (
            f"INSERT INTO {operador_table} "
            "(cedula, nombre_operador, apellido_operador, codigo_dinomi, nombreCompleto, usuario, correo, id_lider ) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )

        if existe:
            context = __set_context()
            context.update({"create_operador_form": form})
            print("operador ya existe")
            return context


        nombres = form.cleaned_data["nombres"].upper()
        apellidos = form.cleaned_data["apellidos"].upper()
        usuario = nombres[0].lower() + apellidos.split(" ")[0].title() + apellidos.split(" ")[1].title()
        correo = form.cleaned_data["correo"]
        password = form.cleaned_data["password"]

        values = (
            cedula,
            nombres,
            apellidos,
            form.cleaned_data["codigoDinomi"],
            nombres + " " + apellidos,
            usuario,
            correo,
            form.cleaned_data["lideres"],
        )

        if User.objects.filter(username=usuario).exists():
            typeMessage = "error_message"

            mensaje = "Usuario ya existe en Django"

            context = __set_context()
            context.update({typeMessage: mensaje})
            return context
        
        # Crear el usuario en Django
        user = User.objects.create_user(username=usuario, email=correo, password=password)
        user.first_name = nombres
        user.last_name = apellidos
        user.save()

        # Asignar el grupo OPERADOR
        group = Group.objects.get(name='OPERADOR')
        user.groups.add(group)


        with connection() as conn:
            conn.execute(add_operador, values)
            if conn.rowcount:
                id_request = conn.lastrowid
            conn.close()

        typeMessage = "success_message" if id_request else "error_message"
        mensaje = (
            "Operador registrado correctamente!"
            if id_request
            else "Problemas al registrar el operador."
        )

        context = __set_context()
        context.update({typeMessage: mensaje})
        return context

    else:
        context = __set_context()
        context.update({"create_operador_form": form})
        return context


def __update_operador(data):

    list_lideres = __get_lideres()

    form = base_operador_form(
        data, 
        list_lideres = list_lideres,
        )
    
    if form.is_valid():
        update_operador = (
            f"UPDATE {operador_table} SET "
            "cedula = %s, "
            "nombre_operador = %s, "
            "apellido_operador = %s, "
            "codigo_dinomi = %s, "
            "nombreCompleto = %s, "
            "id_lider = %s "
            "WHERE id = %s"
        )

        nombres = form.cleaned_data["nombres"]
        apellidos = form.cleaned_data["apellidos"]
        id_lider = int(form.cleaned_data["lideres"])

        values = (
            form.cleaned_data["cedula"],
            nombres,
            apellidos,
            form.cleaned_data["codigoDinomi"],
            nombres + " " + apellidos,
            id_lider ,
            form.cleaned_data["id"],
        )

        query_is_successfull = False
        with connection() as conn:
            conn.execute(update_operador, values)
            if conn.rowcount > 0:
                query_is_successfull = True

            conn.close()

        typeMessage = "success_message" if query_is_successfull else "error_message"
        mensaje = (
            f"Información del operador {apellidos} actualizada correctamente!"
            if query_is_successfull
            else f"Problemas al actualizar la información del operador {apellidos}."
        )

        operador_form, historialOperador_form, listId_campana = __get_operador_info(data.get("id"))
        context = {
                "operador_data_form": operador_form,
                "historialOperador_data_form": historialOperador_form,
                "listHistorial": listId_campana,
                typeMessage: mensaje
            }
        return context

    else:
        print("errores en el formulario")
        print(form.errors)
        _, historialOperador_form, listId_campana = __get_operador_info(data.get("id"))
        context = {
                "operador_data_form": form,
                "historialOperador_data_form": historialOperador_form,
                "listHistorial": listId_campana,
            }
        return context


def __update_historialOperador(data):
    listId_historial_newRegister = __count_historial_entries(data)

    list_companias = __get_compania()
    list_campanas = __getCampanas(data.get("compania"))

    form = edit_operador_form(
        data, 
        list_historial_newRegister = listId_historial_newRegister, 
        list_companias = list_companias,
        list_campanas = list_campanas,
        )
    
    if form.is_valid():
        list_historial = __get_historial_operador(data.get("id"), estado=False)
        listfechas = [historial[3] for historial in list_historial]
        listId_campanas = [historial[0] for historial in list_historial]

        operador_id = form.cleaned_data["id"]

        insert_value = ""

        now = datetime.now().date()

        for campana_Id in listId_historial_newRegister:
            cuota = form.cleaned_data[f"historialCuota{campana_Id}"]
            fecha = now.strftime('%Y-%m-%d')

            if campana_Id in listId_campanas:
                index = listId_campanas.index(campana_Id)
                fecha = listfechas[index].strftime('%Y-%m-%d')

            insert_value += f"({operador_id}, {campana_Id}, '{fecha}', {cuota }, 1), "
                
        insert_value = insert_value.rstrip(", ")

        update_historialOperador = (
            f"INSERT INTO {historialOperador_table} "
            "(id_operador, id_campana, fecha, cuota, estado) "
            f"VALUES {insert_value} "
            "ON DUPLICATE KEY UPDATE estado = VALUES(estado), cuota = VALUES(cuota) "
        )
        
        query_is_successfull = False
        with connection() as conn:
            conn.execute(update_historialOperador)
            if conn.rowcount > 0:
                query_is_successfull = True

            conn.close()

        typeMessage = "success_message" if query_is_successfull else "error_message"
        mensaje = (
            "Información del historial del operador actualizada correctamente!"
            if query_is_successfull
            else "Problemas al actualizar la información del historial del operador."
        )

        operador_form, historialOperador_form, listId_campana = __get_operador_info(data.get("id"))
        context = {
                "operador_data_form": operador_form,
                "historialOperador_data_form": historialOperador_form,
                "listHistorial": listId_campana,
                typeMessage: mensaje
            }
        return context

    else:
        print("errores en el formulario")
        print(form.errors)
        operador_form, _, _ = __get_operador_info(data.get("id"))
        context = {
                "operador_data_form": operador_form,
                "historialOperador_data_form": form,
                "listHistorial":listId_historial_newRegister
            }
        return context
    

def __count_historial_entries(post_data):
    # Inicializar un contador para las filas de historial
    historial_count = []
    # Recorrer las claves del QueryDict y buscar claves que comiencen con 'historialId'
    for key in post_data.keys():
        if key.startswith('historialId'):
            historial_count.append(int(key[len('historialId'):]))
    return historial_count

def __checkPOST(req):
    if req.method == "POST":
        body = req.POST

        if "create_new_operador" in body:
            result = __create_new_operador(body)
            return ( result, "view")

        if "update_operador_data" in body:
            result = __update_operador(body)
            return (result, "edit")
        
        if "update_historialOperador_data" in body:
            result = __update_historialOperador(body)
            return (result, "edit")

    if req.method == "GET":
        params = req.GET

        if "operador_id" in params:
            operador_id = params.get("operador_id")

            if not operador_id:
                raise Http404("ID del operador no proporcionado")

            operador_form, historialOperador_form, listId_campana = __get_operador_info(operador_id)
            context = {
                "operador_data_form": operador_form,
                "historialOperador_data_form": historialOperador_form,
                "listHistorial": listId_campana,
            }
            return (context, "edit")

        else:
            # raise Http404("ID del operador no proporcionado")
            return (__set_context(), "view")


def __set_context():
    operadores = __get_operadores()
    list_lideres = __get_lideres()

    context = {
        "operadores": operadores,
        "create_operador_form": create_operador_form(list_lideres = list_lideres ),
    }
    return context


def process_operador_page(req):
    context, typeAction = __checkPOST(req)

    if typeAction == "edit":
        return render(req, template_edit, context)
    
    if typeAction == "view":
        return render(req, template_name, context)
    else:
        return redirect('')
