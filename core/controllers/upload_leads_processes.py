from ..forms.upload_file_form.select_excel_columns_form import select_excel_columns_form
from ..forms.upload_file_form.upload_base_form import upload_base_form

from ..AWS.RDS import connection
from ..AWS.S3 import upload_file
from ..utils import excel
from ..utils.database.data_processes import lead_fields
from .upload_files_processes import upload_files_processes as ufp

import os

from django.shortcuts import render, redirect

template_name = 'uploading_files/upload_leads.html'
files_path = os.path.join('core', 'excel_files', 'leads')


def __process_file(req):
    body = req.POST
    files = req.FILES

    form = upload_base_form(body, files)

    if form.is_valid():
        columns_select_fields = excel.get_columns_info(files['file'])

        atributos = ufp.get_db_table_columns_choices('cliente')
        atributos += [("celular", "celular"), ("correo", "correo"), ("telefono", "telefono"), ("nombre_completo", "nombre_completo"), ("cupo_pycca", "cupo pycca")]

        columns_form = select_excel_columns_form(
            columns=columns_select_fields, choices=atributos, typeFile = "dinomi")

        columns_info = zip(columns_select_fields.keys(),
                           columns_select_fields.values(), columns_form)

        file_uploading_data = {
            'campaigns': body['choices'] if 'choices' in body else None
        }

        excel_path = os.path.join(
            'core', 'excel_files', 'leads', files['file'].name)
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
    selected_columns_data = excel.process_columns_data(data, 'Leads')
    selected_columns_data.update({'username': req.user.username})
    campaign_company_id = selected_columns_data['file_uploading_data']['campaigns'].split('-')

    uploading_is_valid = ufp.validate_uploading(
        selected_columns_data['columns'], 'cedula_cliente', req, template_name, context)

    if uploading_is_valid:
        excel.remove_all_files(files_path)
        return uploading_is_valid

    file_path = os.path.join('core', 'excel_files',
                             'leads', data['excel-file'])

    result = ufp.store_matched_columns_in_database(
        columns_matched=selected_columns_data['columns'],
        process_name='leads',
        file=file_path,
        campaign_company_id=campaign_company_id
    )
    excel.remove_file(file_path)

    context = __set_context()
    context.update(result)

    return render(req, template_name, context)


def __checkPOST(req):
    if req.method == 'POST':
        body = req.POST

        if 'process-leads-file' in body:
            result = __process_file(req)

        if 'select-columns' in body:
            result = __process_columns_info(req)

        return result

def __set_context():
    context = {
        'page_title': 'Campañas registradas',
        'upload_file_form': upload_base_form(),
        #'choices_name': 'Campañas',
        #'campaign_required': True
    }

    return context

def process_upload_leads_page(req):
    post = __checkPOST(req)
    if post:
        return post

    excel.remove_all_files(files_path)

    context = __set_context()

    return render(req, template_name, context)
