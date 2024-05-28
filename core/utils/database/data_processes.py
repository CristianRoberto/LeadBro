import math

from . import SQL_field_casting as sfc
from ...AWS.RDS import connection


lead_fields = [
    ("", "No importar"),
    ("cedula_cliente", "cedula_cliente"),
    ("nombres_completos", "nombres_completos"),
    ("nombres", "nombres"),
    ("apellidos", "apellidos"),
    ("telf", "telf"),
    ("valor_facturado", "valor_facturado"),
    ("producto", "producto"),
    ("fecha", "fecha"),
    ("operador", "operador"),
    ("estado", "estado"),
    ("email", "email"),
    ("ciudad", "ciudad"),
    ("fecha_y_hora", "fecha_y_hora"),
    ("duracion_llamada", "duracion_llamada"),
    ("codigo_dinomi", "codigo_operador_dinomi"),
    ("tipologia", "tipologia"),
    ("campanha", "campaña"),
    ("valor_sin_iva", "valor_sin_iva"),
    ("tipo_de_venta", "tipo_de_venta"),
    ("categoria_producto", "categoria_producto"),
    ("marca_temporal", "marca_temporal"),
]

lead_fields = sorted(lead_fields, key=lambda tuple: tuple[0])


leads_table_fields = {
    "apellidos": "apellidos",
    "cedula_cliente": "cedula",
    "ciudad": "ciudad",
    "codigo_dinomi": "codigo_dinomi",
    "duracion_llamada": "duracion_llamada",
    "email": "email1",
    "estado": "estado",
    "fecha": "fecha_creacion",
    "fecha_y_hora": "fecha_hora",
    "nombres": "nombres",
    "nombres_completos": "nombres_completos",
    "operador": "nombre_operador",
    "producto": "producto",
    "telf": "tel1",
    "tipologia": "tipologia",
    "valor_facturado": "valor",
    "valor_sin_iva": "valor_sin_iva",
    "tipo_de_venta": "tipo_venta",
    "categoria_producto": "producto_categoria",
    "marca_temporal": "marca_temporal",
}

cliente_table_fields = {
    "id": "id",
    "cedula": "cedula",
    "nombres": "nombres",
    "apellidos": "apellidos",
    "fecha_nacimiento": "fecha_nacimiento",
    "edad": "edad",
    "genero": "genero",
    "ciudad": "ciudad",
    "provincia": "provincia",
    "estado_civil": "estado_civil",
    "cupo_pycca": "cupo_pycca",
    "fecha_ultima_transaccion_pycca": "fecha_ultima_transaccion_pycca",
    "direccion_domicilio": "direccion_domicilio",
    "condicion_laboral": "condicion_laboral",
    "dependencia_laboral": "dependencia_laboral",
    "antiguedad_laboral": "antiguedad_laboral",
    "lugar_trabajo": "lugar_trabajo",
    "direccion_trabajo": "direccion_trabajo",
    "cargas_familiares": "cargas_familiares",
    "rfm_pycca": "rfm_pycca",
    "ruc": "ruc",
    "salario": "salario",
    "tipificacion": "tipificacion",
}


def _set_names_and_last_names(names: str):
    a = names.split(" ")
    middle = math.trunc(len(a) / 2)
    final_names = " ".join(a[:middle])
    last_names = " ".join(a[middle:])

    return {"nombres": final_names, "apellidos": last_names}


def get_matched_lead_fields(data):
    matched_fields = {k: leads_table_fields[k] for k in data if k in leads_table_fields}
    return matched_fields


def get_matched_cliente_fields(data):    
    matched_fields = {
        k: cliente_table_fields[k] for k in data if k in cliente_table_fields
    }

    return matched_fields


def _get_row(row, columns_data: dict, table_fields):
    new_row = {
        value: row[key]
        for key, value in columns_data.items()
        if key in table_fields and key in row
    }

    return new_row


def get_lead_row(row, columns_data: dict):
    table_fields = {
        "categoria_producto",
        "duracion_llamada",
        "estado",
        "fecha",
        "fecha_y_hora",
        "operador",
        "producto",
        "tipo_de_venta",
        "valor_facturado",
        "valor_sin_iva",
        "marca_temporal",
    }
    new_row = _get_row(row, columns_data, table_fields)

    return new_row


def get_operator_row(row, columns_data: dict):
    table_fields = {"operador", "codigo_dinomi"}
    new_row = _get_row(row, columns_data, table_fields)

    complete_names = _set_names_and_last_names(new_row["nombre_operador"])
    complete_names["nombre_operador"] = complete_names.pop("nombres")
    complete_names["apellido_operador"] = complete_names.pop("apellidos")

    new_row.update(complete_names)
    del new_row["nombre_operador"]

    return new_row


def get_tipologia_row(row, columns_data: dict):
    table_fields = {"tipologia"}
    new_row = _get_row(row, columns_data, table_fields)

    return new_row


def get_client_row(row, columns_data: dict):
    table_fields = {
        "cedula_cliente",
        "nombres_completos",
        "nombres",
        "apellidos",
        "telf",
        "email",
        "ciudad",
    }
    new_row = _get_row(row, columns_data, table_fields)

    if "nombres_completos" in new_row:
        complete_names = _set_names_and_last_names(new_row["nombres_completos"])

        new_row.update(complete_names)
        del new_row["nombres_completos"]

    if "cedula" in new_row:
        new_row["cedula"] = sfc.make_dni(new_row["cedula"])

    return new_row


def generate_insert_query(row:dict, fields: list, db_table):
    if db_table == "cliente" and "nombre_completo" in fields and all(x not in fields for x in ["nombres", "apellidos"]):
        nombres, apellidos = sfc.check_field_to_sql_format(row["nombre_completo"], "nombre_completo")
        row["nombres"] = nombres
        fields += ["nombres"] 
        if apellidos: 
            row["apellidos"] = apellidos 
            fields += ["apellidos"] 

        del row["nombre_completo"]
        fields.remove("nombre_completo")


    db_fields = []
    on_duplicated_query = ""
    row_values = []

    list_errores = []
    
    for field in fields:
        field_value = sfc.check_field_to_sql_format(row[field], field)
        if field == "cedula" and field_value == "ERROR":
            list_errores += [f"Problema critico con con el cliente con id {cedula}"]
            return [None, None, list_errores]
        if field_value == "ERROR":
            cedula = row["cedula"] if "cedula" in row else row["id_cliente"]
            list_errores += [f"Problemas en el campo {field} del cliente con id {cedula}"]
            continue
        on_duplicated_query += f"{field} = VALUES({field}),"
        row_values.append(field_value)
        db_fields.append(field)

    if len(db_fields) < 2 and db_table != "cliente":
        return [None, None, list_errores]
    
    db_fields_string = ", ".join(db_fields)
    on_duplicated_query = on_duplicated_query.rstrip(",")
    placeholders = ", ".join(["%s"] * len(row_values))

    insert_query = f"""
        INSERT INTO {db_table} ({db_fields_string})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {on_duplicated_query}"""

    return [insert_query, tuple(row_values), list_errores]


def generate_update_query(row:dict, fields: list, db_table: str, key: str):
    update_query = f"UPDATE {db_table} SET "
    row_values = []
    key_value = None

    for field in fields:
        field_value = sfc.check_field_to_sql_format(row[field], field)
        if field == key:
            key_value = field_value
        else:
            update_query += f"{field} = %s, "
            
            row_values.append(field_value)

    update_query = update_query.rstrip(", ")

    update_query += f" WHERE {key} = %s"
    row_values.append(key_value)
    return [update_query, tuple(row_values)]


def update_db_spreadsheet_rowcount(spreadsheet_id: str, row_count: int):
    query = "UPDATE spreadsheets " "SET num_filas = %s " "WHERE id = %s"
    values = (row_count, spreadsheet_id)

    with connection() as conn:
        conn.execute(query, values)
