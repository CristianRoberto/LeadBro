import ast
import pandas as pd
import os
import multiprocessing
import functools


def check_if_path_exists(func):
    @functools.wraps(func)
    def wrapper(path, *args, **kwargs):
        if os.path.exists(path):
            return func(path, *args, **kwargs)

    return wrapper


def get_columns_info(file):
    data = pd.read_excel(file)
    return data.count().to_dict()


def upload_file(path, file):
    directory, _ = os.path.split(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

@check_if_path_exists
def remove_file(file_path):
    os.remove(file_path)


@check_if_path_exists
def _remove_in_parallel(directory):
    for archivo in os.listdir(directory):
        os.remove(os.path.join(directory, archivo))


def remove_all_files(directory):
    process = multiprocessing.Process(
        target=_remove_in_parallel, args=(directory,))
    process.start()


def process_columns_data(data, base_type=None):
    file_uploading_data_dict = ast.literal_eval(data['file_uploading_data'])

    if base_type:
        file_uploading_data_dict.update({'base_type': base_type})

    columns = {}
    for column_name, value in data.items():
        if column_name.startswith('column-') and value:
            name = column_name.replace('column-', '')
            columns[name] = value

    selected_columns_data = {
        'columns': columns,
        'file_uploading_data': file_uploading_data_dict
    }

    return selected_columns_data


def filter_and_rename_columns(columns, file=None, dataframe=None):
    data = None
    if file:
        data = pd.read_excel(file, dtype=str)
    if dataframe is not None:
        data = dataframe

    columns_to_keep = columns.keys()

    filtered_data = data.filter(columns_to_keep)
    filtered_data.rename(columns=columns, inplace=True)
    filtered_data.dropna(how='all', inplace=True)
    filtered_data.fillna('NULL', inplace=True)

    return filtered_data
