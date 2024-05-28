from datetime import datetime
import pandas as pd
import json

from ...AWS.RDS import connection
from .api.google_sheets_manager import google_worksheet
from ..upload_files_processes.upload_files_processes import store_matched_columns_in_database as store
from ...utils.database.data_processes import update_db_spreadsheet_rowcount


def __filter_and_update_columns(
        columns_matched: dict,
        columns_to_update: tuple,
        column_key: str,
        df: pd.DataFrame
):
    filtered_matched_columns = {
        key: columns_matched[key] for key in columns_to_update
    }
    filtered_matched_columns.update({column_key: columns_matched[column_key]})

    store(
        columns_matched=filtered_matched_columns,
        process_name='update_table_values',
        df=df,
        table_name='leads',
        key=columns_matched[column_key],
        disable_metrics=True
    )


def _insert_leads_from_ws_range(
    ws: google_worksheet,
    columns_matched: dict,
    range_: list,
    columns_to_update: tuple = None,
    column_key: str = None
):
    ws_data = ws.get_range_as_dataframe(range_)
    insert_result = store(
        columns_matched=columns_matched,
        process_name='leads',
        df=ws_data,
    )

    if insert_result and columns_to_update and column_key:
        new_columns_tuple = columns_to_update + (column_key,)
        data_to_update = ws.get_headers_elements(new_columns_tuple)
        df_to_update = pd.DataFrame(data_to_update)

        __filter_and_update_columns(
            columns_matched, new_columns_tuple, column_key, df_to_update)

    return insert_result


def store_rows_in_db(
    data: dict,
    first_time: bool = False,
    columns_to_update: tuple = None
):
    id_ = data.get('id')
    stored_row_count = data.get('num_filas')
    columns = data.get('columnas')

    ws = google_worksheet(id_)
    current_row_count = ws.row_count

    if not stored_row_count:
        stored_row_count = current_row_count

    if not first_time and (current_row_count > stored_row_count):
        start_row_range = stored_row_count + 1
        range_ = [f'A{start_row_range}:Z{current_row_count}']
        insert_result = _insert_leads_from_ws_range(
            ws, columns, range_, columns_to_update, 'Marca temporal')

        if insert_result:
            update_db_spreadsheet_rowcount(id_, current_row_count)

    elif first_time and (stored_row_count > 1):
        range_ = [f'A2:Z{current_row_count}']
        insert_result = _insert_leads_from_ws_range(ws, columns, range_)


def sync_sheets():
    time_str = datetime.now().strftime('%H:%M')
    query = 'SELECT id, columnas, num_filas FROM spreadsheets WHERE rango_cortes LIKE %s;'
    value = '%' + time_str + '%'

    with connection() as conn:
        conn.execute(query, (value,))
        rows = conn.fetchall()
        for id, columns, row_count in rows:
            data = {
                "id": str(id),
                "columnas": json.loads(str(columns)),
                "num_filas": int(row_count)
            }
            columns_to_update = ('VALOR FACTURADO', 'MONTO FACTURADO SIN IVA')
            store_rows_in_db(data, columns_to_update=columns_to_update)
