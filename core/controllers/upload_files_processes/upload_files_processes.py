import pandas as pd
from collections import defaultdict

from pandarallel import pandarallel

from ...AWS.RDS import connection
from ...utils import excel

from django.shortcuts import render, redirect


def _get_campaign_company_id_by_name(campaign_name: str):
    query = 'SELECT id, id_compania FROM campana WHERE nombre = %s'

    campaign_id, company_id = '', ''
    with connection() as conn:
        conn.execute(query, (campaign_name,))
        for campaign, company in conn:
            campaign_id = campaign
            company_id = company

    return [campaign_id, company_id]


def _get_campaign_company_ids_by_row(row):
    campaign_field_names = {'campana', 'campaña', 'campanha', 'campaign'}

    for key, value in row.items():
        if key.lower() in campaign_field_names:
            campaign_name = value
            ids = _get_campaign_company_id_by_name(campaign_name)
            return ids

    return [None, None]


def basic_query_executor(
    row,
    fields,
    table_name,
    query_type: str = None,
    **kwargs
):
    from ...AWS.RDS import connection
    from ...utils.database import data_processes

    query_generator = {
        'INSERT': data_processes.generate_insert_query,
        'UPDATE': data_processes.generate_update_query
    }

    query_function = query_generator[query_type]

    insert_tipology_query, row_values = query_function(
        row, fields, table_name, **kwargs)

    count_insert = 0
    count_update = 0
    success = False

    with connection() as conn:
        conn.execute(insert_tipology_query, row_values)
        if conn.rowcount == 1:
            count_insert += 1
            success = True

        if conn.rowcount == 0 or conn.rowcount == 2:
            count_update += 1
            success = True

    return success


def update_table_values(row:dict, fields:list, table_name, key):
    from ...utils.database import data_processes

    if table_name == 'leads':
        fields = data_processes.get_matched_lead_fields(fields)
        row = data_processes.get_lead_row(row, fields)
    
    if table_name == 'cliente':
        fields = data_processes.get_matched_cliente_fields(fields)
    
    result = basic_query_executor(
        row, fields.values(), table_name, 'UPDATE', key=key)

    return result

def insert_contact_records(contact_data: list, field, id_cliente):
    from ...AWS.RDS import connection
    from ...utils.database import data_processes
    contact_list = [item for item in contact_data if item != 'NULL']
    verify_contact_query = ""
    typeContact = ""
    data = {}
    typeField = []

    if not contact_list:
        return (True, 0, [])


    if field == "correo":
        typeContact = "correo_cliente"
        typeField = ["correo", "id_cliente"] 
        verify_contact_query = 'SELECT * FROM correo_cliente WHERE id_cliente = %s AND correo = %s limit 1'
        data = {"correo": "", "id_cliente": id_cliente}

    elif field == "celular":
        typeContact = "celular_cliente"
        typeField = ["celular", "id_cliente"]
        verify_contact_query = 'SELECT * FROM celular_cliente WHERE id_cliente = %s AND celular = %s limit 1'
        data = {"celular": "", "id_cliente": id_cliente}

    elif field == "telefono":
        typeContact = "telefono_cliente"
        typeField = ["telefono", "id_cliente"]
        verify_contact_query = 'SELECT * FROM telefono_cliente WHERE id_cliente = %s AND telefono = %s limit 1'
        data = {"telefono": "", "id_cliente": id_cliente}

    else:
        return (False, 0, ["Campo de contacto incorrecto."])

    query_is_successful = False
    count_insert = 0
    count_errors = 0
    list_errors = []
    with connection() as conn:
        for i in range(len(contact_list)):
            conn.execute(verify_contact_query, (id_cliente, contact_list[i]))
            contacto_existente = conn.fetchone()
            if contacto_existente:
                id_contacto = contacto_existente[0]  
                query_is_successful = True
            else:

                data[field] = contact_list[i]      
                #contacto nuevo es registrado
                insert_contact_query, row_values, list_errors = data_processes.generate_insert_query(
                    data, typeField, typeContact)
                                
                if not insert_contact_query:                    
                    return (query_is_successful, count_errors + 1, list_errors)
                
                conn.execute(insert_contact_query, row_values)
                if conn.rowcount == 1:
                    count_insert += 1
                    query_is_successful = True
                
                id_contacto = conn.lastrowid

            if not id_contacto:               
                count_errors +=1
                list_errors += [f"problemas con ejecutar el query del cliente con id: {id_cliente}"]

        
        #conn.commit()

    return (query_is_successful, count_errors, list_errors)

# row es un pandasSeries con los valores de la fila
# fields es una lista con los heads 
def insert_client_records(row, fields, company_id=None):
    from ...AWS.RDS import connection
    from ...utils.database import SQL_field_casting as sfc
    from ...utils.database import data_processes
    row = row.groupby(level=0).apply(list).to_dict()
    exclude_fields = ["celular", "correo", "telefono"]
    
    fields_client = [field for field in fields if (row[field][0] !="NULL") and (field not in exclude_fields)]
    for key in row.keys(): 
        if key not in exclude_fields:
            row[key] = row[key][0]

    fields_client = [field for field in fields if (row[field][0] !="NULL") and (field not in exclude_fields)]
    
    verify_client_query = 'SELECT * FROM cliente WHERE cedula = %s limit 1'
    
    #valida los formatos de la data y genera el query
    insert_client_query, row_values, list_error = data_processes.generate_insert_query(
            row.copy(), fields_client, 'cliente')
    
    query_is_successful = False
    count_insert = 0
    count_update = 0
    count_errors = 0

    if not insert_client_query:
        result = {
            'success': query_is_successful,
            'insert': count_insert,
            'update': count_update,
            'errors': count_errors + 1,# errores por inserts, updates
            'logs': list_error # errores en el formato de la data
        }
        return result
    
    with connection() as conn:
        conn.execute(verify_client_query, (row["cedula"].zfill(10),))
        cliente_existente = conn.fetchone()
        if cliente_existente:
            id_cliente = cliente_existente[0]  
            new_row = row.copy()
            new_row["id"] = id_cliente
            query_is_successful = update_table_values(new_row, ["id"] + fields_client, "cliente", "id")
            count_update +=1  
        else:
            #cliente nuevo es registrado
            conn.execute(insert_client_query, row_values)
            if conn.rowcount == 1:
                count_insert += 1
                query_is_successful = True       

                # Obtener el ID del cliente insertado
            id_cliente = conn.lastrowid

            if not id_cliente:
                query_is_successful= False
                count_errors +=1
                list_error += [f"problemas con ejecutar el query del cliente con cedula: {row['cedula']}"]
        
    if id_cliente:                
        if fields.count('correo') > 0 and query_is_successful:
            data = row["correo"]
            query_is_successful, count_errors_correo, list_error1 = insert_contact_records(data, "correo", id_cliente)            
            count_errors += count_errors_correo
            list_error += list_error1
        
        if fields.count('celular') > 0  and query_is_successful:
            data = row["celular"]
            query_is_successful, count_errors_celular, list_error2 = insert_contact_records(data, "celular", id_cliente)
            count_errors += count_errors_celular
            list_error += list_error2
        
        if fields.count('telefono') > 0 and query_is_successful:
            data = row["telefono"]
            query_is_successful, count_errors_telefono, list_error3 = insert_contact_records(data, "telefono", id_cliente)   
            count_errors += count_errors_telefono
            list_error += list_error3
    
    else:
        count_insert = 0
        count_errors +=1

    result = {
        'success': query_is_successful,
        'insert': count_insert,
        'update': count_update,
        'errors': count_errors,# errores por inserts, updates
        'logs': list_error # errores en el formato de la data
    }
    return result


def insert_leads_records(
    row,
    fields,
    campaign_company_id: list = None,
):
    from ...AWS.RDS import connection
    from ...utils.database import data_processes

    matched_fields = data_processes.get_matched_lead_fields(fields)
    client_row = data_processes.get_client_row(row, matched_fields)
    lead_row = data_processes.get_lead_row(row, matched_fields)
    operator_row = data_processes.get_operator_row(row, matched_fields)
    tipologia_row = data_processes.get_tipologia_row(row, matched_fields)

    if campaign_company_id:
        campaign_id, company_id = campaign_company_id
    else:
        campaign_id, company_id = _get_campaign_company_ids_by_row(row)

    lead_row.update({
        'cedula_cliente': client_row['cedula'],
        'id_campana': campaign_id if campaign_id else 'Null'
    })

    insert_lead_query, lead_row_values = data_processes.generate_insert_query(
        lead_row, lead_row.keys(), 'leads')

    if tipologia_row:
        tipology = basic_query_executor(
            tipologia_row, tipologia_row.keys(), 'tipologia', 'INSERT')

    if operator_row:
        operator = basic_query_executor(
            operator_row, operator_row.keys(), 'operador', 'INSERT')

    client_result = None
    query_is_successful = False

    #with connection() as conn:
    #    client_result = insert_client_records(
    #        client_row, client_row.keys(), company_id=company_id)

    #    conn.execute(insert_lead_query, lead_row_values)
    #    if conn.lastrowid:
    #        query_is_successful = True

    result = {
        'success': query_is_successful,
        'client': client_result
    }

    return result


def store_matched_columns_in_database(
    columns_matched,
    process_name: str,
    file: str = None,
    df: pd.DataFrame = None,
    disable_metrics: bool = False,
    **kwargs
):
    if file:
        data_frame = excel.filter_and_rename_columns(
            columns_matched, file=file)

    if df is not None:
        data_frame = excel.filter_and_rename_columns(
            columns_matched, dataframe=df)

    data_frame.fillna("", inplace=True)    
    fields = list(columns_matched.values())
    query_functions = {
        'cliente': insert_client_records,
        'leads': insert_leads_records,
        'update_table_values': update_table_values
    }
    selected_query_function = query_functions[process_name]

    pandarallel.initialize()
    results = data_frame.apply(
        selected_query_function,
        args=(fields,),
        **kwargs,
        axis=1,
        result_type='expand'
    )
    #results = data_frame.parallel_apply(
    #    selected_query_function,
    #    args=(fields,),
    #    **kwargs,
    #    axis=1,
    #    result_type='expand'
    #)

    if not disable_metrics:
        metrics = __get_file_uploading_metrics(results, process_name)

        return metrics
    else:
        return True


def __process_clients_results(df: pd.DataFrame):
    success = df['success'].all()
    errors = df['errors'].sum()
    inserted = df['insert'].sum()
    updated = df['update'].sum()
    logs = df['logs'].sum()

    client_metrics = {
        'success': success,
        'records': {
            'errores': errors,
            'inserted': inserted,
            'updated': updated,
        },
        'logs': logs
    }

    return [client_metrics]


def __process_leads_results(df: pd.DataFrame):
    df_client = pd.json_normalize(df['client'])
    client_metrics = __process_clients_results(df_client)
    total_leads = len(df.index)

    return [total_leads, client_metrics[0]]


def __get_file_uploading_metrics(result, process_name):
    process_result = {
        'cliente': __process_clients_results,
        'leads': __process_leads_results
    }

    process_function = process_result[process_name]
    metrics = process_function(result)
    total_result = {
        'file_uploaded': True,
        'client_metrics': metrics[-1]
    }

    if len(metrics) > 1:
        total_result['leads_metrics'] = metrics[0]

    return total_result


def get_db_table_columns_choices(table_name):
    COLUMN_NAME = 0
    with connection() as conn:
        query = f'SHOW COLUMNS FROM {table_name}'
        conn.execute(query)
        result = [('', 'No importar')]
        result += [(column[COLUMN_NAME], column[COLUMN_NAME])
                   for column in conn if column[COLUMN_NAME] != 'id']
        
        # No sort to keep database order
        #sorted_result = sorted(result, key=lambda tuple: tuple[0])

    return result


def __get_duplicated_dict_values(columns: dict, exceptions: list):
    values_dict = defaultdict(list)

    for key, value in columns.items():
        values_dict[value].append(key)

    reverse_dict = {item: key for key, list in values_dict.items() if len(
        list) > 1 and key not in exceptions for item in list}

    return reverse_dict


def check_repeated_matches(
    matched_columns: dict,
    exceptions: list,
    req,
    template_name: str,
    context: dict = None
):
    repeated_matches = __get_duplicated_dict_values(matched_columns, exceptions)

    if repeated_matches:
        repeated_columns_msg = ''
        for key, value in repeated_matches.items():
            repeated_columns_msg += f'{key}: {value}\n'

        msg = (
            'Debe seleccionar unicamente un campo para cada columna.\n'
            'Se encontraron los siguientes campos repetidos:\n'
            f'{repeated_columns_msg}'
        )
        context.update({'upload_err_msg': msg})
        return render(req, template_name, context)

    return


def check_required_db_file(
    matched_columns: dict,
    required_field: str,
    req,
    template_name: str,
    context: dict
):
    values = matched_columns.values()
    if not required_field in values:
        msg = f'¡{required_field} es obligatorio!'
        context.update({'upload_err_msg': msg})

        return render(req, template_name, context)

    return


def validate_uploading(
    matched_columns: dict,
    required_field: str,
    exceptions: list,
    req,
    template_name: str,
    context: dict
):
    not_required_field = check_required_db_file(
        matched_columns, required_field, req, template_name, context)

    if not_required_field:
        return not_required_field

    render_if_repeated_match = check_repeated_matches(
        matched_columns, exceptions, req, template_name, context)

    if render_if_repeated_match:
        return render_if_repeated_match

    return
