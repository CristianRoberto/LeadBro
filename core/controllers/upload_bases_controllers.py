from ..forms.upload_file_form.select_excel_columns_form import select_excel_columns_form
from ..forms.upload_file_form.upload_base_form import upload_base_form

from ..AWS.RDS import connection
from ..AWS.S3 import upload_file
from ..utils import excel
from .upload_files_processes import upload_files_processes as ufp

import os

from django.shortcuts import render, redirect

template_name = 'uploading_files/upload_customers.html'
files_path = os.path.join('core', 'excel_files', 'bases')

def __get_customers():
    with connection() as conn:
        conn.execute('SELECT id, nombre FROM compania')
        result = [i for i in conn]

    return result


def __process_file(req):
    body = req.POST
    files = req.FILES

    if 'choices' in body:
        SELECTION_ID = body['choices']
        choices_list = [(SELECTION_ID, '')]
        form = upload_base_form(body, files, choices_list=choices_list)
    else:
        form = upload_base_form(body, files)

    if form.is_valid():
        columns_select_fields = excel.get_columns_info(files['file'])
        user_columns = ufp.get_db_table_columns_choices('cliente')
        
        #add choices for
        user_columns += [("celular", "celular"), ("correo", "correo"), ("telefono", "telefono"), ("nombre_completo", "nombre_completo")]

        columns_form = select_excel_columns_form(
            columns=columns_select_fields, choices=user_columns)
        
        columns_info = zip(columns_select_fields.keys(),
                           columns_select_fields.values(), columns_form)

        file_uploading_data = {
            'customers': body['choices'][0] if 'choices' in body else None
        }

        excel_path = os.path.join(
            'core', 'excel_files', 'bases', files['file'].name)
        excel.upload_file(excel_path, files['file'])

        context = __set_context()
        context.update({
            'columns_info': columns_info,
            'file_uploading_data': file_uploading_data,
            'excel_file': files['file'].name
        })

        return render(req, template_name, context)
    else:
        print(form.errors)
        return redirect(req.path)


def __process_columns_info(req):
    data = req.POST
    context = __set_context()
    # create a json with column excel name as key and the chosen opcion selected as value
    selected_columns_data = excel.process_columns_data(data, 'Clientes')
    selected_columns_data.update({'username': req.user.username})

    # de la data de cliente, solo el correo, celular y telefono se pueden repetir
    exclude_values = ["correo", "celular", "telefono"]
    filtered_columns = {k: v for k, v in selected_columns_data['columns'].items()} 
    #Check id cedula has been selected
    uploading_is_not_valid = ufp.validate_uploading(
        filtered_columns, 'cedula', exclude_values, req, template_name, context)

    if uploading_is_not_valid:
        excel.remove_all_files(files_path)
        return uploading_is_not_valid

    file_path = os.path.join('core', 'excel_files',
                             'bases', data['excel-file'])

    result = ufp.store_matched_columns_in_database(
        columns_matched=selected_columns_data['columns'],
        process_name='cliente',
        file=file_path,
        company_id=selected_columns_data['file_uploading_data']['customers']
    )
    excel.remove_file(file_path)

    context = __set_context()
    context.update(result)

    return render(req, template_name, context)


def __set_context():
    customers = __get_customers()
    context = {
        'page_title': 'Subir Clientes',
        'upload_file_form': upload_base_form(),
    }

    return context


def __checkPOST(req):
    if req.method == 'POST':
        body = req.POST

        if 'process-leads-file' in body:
            result = __process_file(req)

        if 'select-columns' in body:
            result = __process_columns_info(req)

        return result


def process_upload_customers_page(req):
    post = __checkPOST(req)
    if post:
        return post

    excel.remove_all_files(files_path)

    context = __set_context()

    return render(req, template_name, context)
