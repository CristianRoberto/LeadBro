import json

from ...AWS.RDS import connection
from .api.google_sheets_manager import google_worksheet
from ...forms.sync_google_sheets_form import sync_google_sheet_form
from ...forms.upload_file_form.select_excel_columns_form import select_excel_columns_form
from ... import tasks

from ...utils.database import data_processes
from ...utils.database.data_processes import lead_fields
from ...utils import excel


from django.shortcuts import render, redirect

template_name = 'google_drive_sync.html'
sheet = google_worksheet()


def _delete_spreadsheet(req):
    id = req.POST['id']
    query = 'DELETE FROM spreadsheets WHERE id = %s'

    query_is_successful = False
    with connection() as conn:
        conn.execute(query, (id,))
        if conn.rowcount:
            query_is_successful = True

    return redirect(req.path)


def _get_spreadsheets():
    query = 'SELECT * FROM spreadsheets'
    with connection() as conn:
        conn.execute(query)
        result = [i for i in conn]

    return result


def _zip_spreadsheets_and_forms(spreadsheets):
    sh_to_edit = [sync_google_sheet_form(initial={
        'spreadsheet_id': spreadsheet[0],
        'spreadsheet_name': spreadsheet[1],
        'cutting_time_range': spreadsheet[2]
    }) for spreadsheet in spreadsheets]

    spreadsheets_info = zip(spreadsheets, sh_to_edit)

    return spreadsheets_info


def _process_add_sh_form(req):
    data = req.POST
    form = sync_google_sheet_form(data)
    if form.is_valid():
        sheet.setup_google_sheet(form.cleaned_data['spreadsheet_id'])
        sheet_columns = sheet.get_columns()

        columns_form = select_excel_columns_form(
            columns=sheet_columns, choices=lead_fields)

        columns_info = zip(sheet_columns.keys(), columns_form)
        context = {
            'spreadsheet_form': sync_google_sheet_form(),
            'columns_info': columns_info,
            'file_uploading_data': {
                'spreadsheet_id': form.cleaned_data['spreadsheet_id'],
                'spreadsheet_name': form.cleaned_data['spreadsheet_name'],
                'cutting_time_range': form.cleaned_data['cutting_time_range']
            }
        }

        return render(req, template_name, context)
    else:
        print(form.errors)
        return redirect(req.path)


def _add_spreadsheet(data):
    form = sync_google_sheet_form(data['file_uploading_data'])
    if form.is_valid():
        columns_to_str = json.dumps(data['columns'])
        data_to_insert = {
            'id': form.cleaned_data['spreadsheet_id'],
            'nombre': form.cleaned_data['spreadsheet_name'],
            'rango_cortes': form.cleaned_data['cutting_time_range'],
            'columnas': columns_to_str,
            'num_filas': sheet.row_count
        }

        insert_sh_query, values = data_processes.generate_insert_query(
            data_to_insert, data_to_insert.keys(), 'spreadsheets')

        query_is_successful = False
        with connection() as conn:
            conn.execute(insert_sh_query, values)
            if conn.rowcount == 1 or conn.rowcount == 0:
                query_is_successful = True

        return query_is_successful


def _process_columns_info(req):
    data = req.POST
    selected_columns_data = excel.process_columns_data(data)
    selected_columns_data.update({'username': req.user.username})
    result = _add_spreadsheet(selected_columns_data)

    if result:
        ws_data = {
            'id': selected_columns_data['file_uploading_data']['spreadsheet_id'],
            'columnas': selected_columns_data['columns']
        }
        tasks.store_sheets_leads(ws_data, True)
        return redirect(req.path)


def _checkPOST(req):
    if req.method == 'POST':
        body = req.POST

        if 'add_spreadsheet' in body:
            result = _process_add_sh_form(req)

        if 'select-columns' in body:
            result = _process_columns_info(req)

        if 'delete-spreadsheet' in body:
            result = _delete_spreadsheet(req)

        if 'update-spreadsheet-data' in body:
            result = None

        return result


def process_google_sheet_page(req):
    post = _checkPOST(req)
    if post:
        return post

    spreadsheets = _get_spreadsheets()
    spreadsheets_info = _zip_spreadsheets_and_forms(spreadsheets)

    context = {
        'spreadsheet_form': sync_google_sheet_form(),
        'spreadsheets_info': spreadsheets_info
    }

    return render(req, template_name, context)
