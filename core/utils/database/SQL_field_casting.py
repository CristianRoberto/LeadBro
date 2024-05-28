import re
from dateutil.parser import parse
from . import typesData as TD
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


def is_date_format(string: str):
    date_regex = r"^(?:(?:\d{4}[/-]\d{2}[/-]\d{2})|(?:\d{2}[/-]\d{2}[/-]\d{4}))(?:\s\d{2}:\d{2}:\d{2})?$"

    return bool(re.match(date_regex, string))


def check_money_value(value: str):
    # Verifica si el valor es un número válido
    money_regex = r"^[-]?[£€$]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+(?:\.\d{2})?)$"
    match = re.match(money_regex, value)
    return match.group(1) if match else "ERROR"


def check_valid_mail_address(string: str):
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    return string if bool(re.match(email_regex, string)) else "ERROR"


def set_gender(gender: str):
    gender = gender.lower()
    males = {"hombre", "masculino", "man", "male"}
    females = {"mujer", "femenino", "woman", "female"}

    if gender in males:
        return "MASCULINO"

    elif gender in females:
        return "FEMENINO"
    else:
        return "NS"


def split_nombre_completo(full_name):
    parts = full_name.split(" ")
    if len(parts) == 2:  # Asumiendo que siempre hay al menos un nombre y un apellido
        nombres = " ".join(parts[:-1])
        apellidos = parts[-1]  # El último nombre se considera el apellido

    elif (
        len(parts) >= 3
    ):  # Asumiendo que siempre hay al menos un nombre y dos apellidos
        nombres = " ".join(parts[: len(parts) - 2])
        apellidos = " ".join(parts[-2:])  # El último nombre se considera el apellido
    else:
        nombres = full_name  # Si solo hay un nombre, no hay apellidos
        apellidos = ""
    return [nombres, apellidos]


def convert_to_sql_date_format(string: str):
    date_object = parse(string)
    if date_object.time() == datetime.min.time():
        sql_date_format = date_object.date().strftime("%Y-%m-%d")

    else:
        sql_date_format = date_object.strftime("%Y-%m-%d %H:%M:%S")

    return sql_date_format


def convert_to_sql_decimal_format(string: str):
    decimal_value = Decimal(string.replace(",", ""))

    decimal_value = decimal_value.quantize(Decimal(".01"), rounding=ROUND_HALF_UP)

    return decimal_value


def check_phone_number(value: str, field: str = None):

    match field:
        case "celular":
            if len(value) <= 10 and value.isdigit():
                return value.zfill(10)
            if len(value) <=15:
                return value[-10:]
            else:
                return "ERROR"
        case "telefono":
            return value if len(value) <= 10 and  value.isdigit() else "ERROR"

    return "ERROR"

def check_ciudad( ciudad:str ):
    ciudad = ciudad.upper()
    return ciudad if ciudad in TD.LIST_CIUDAD else "ERROR"

def check_ruc(value: str):
    if not value.isdigit() or len(value) != 13:
        return "ERROR"
    else:
        return value
        

def make_dni(value):
    string = str(value)
    if len(string) < 10 and string[0] != "0":
        return "0" + string
    return string


def check_field_to_sql_format(value: str, field: str = None):
    casted_value = str(value)

    match field:
        case "nombre_completo":
            casted_value = split_nombre_completo(value)
        
        case "cedula":
            casted_value = str(value).zfill(10)

        case "celular":
            casted_value = check_phone_number(value, field)

        case "telefono":
            casted_value = check_phone_number(value, field)

        case "correo":
            casted_value = check_valid_mail_address(value)

        case "genero":
            casted_value = set_gender(value)

        case "cargas_familiares":
            casted_value = int(value) if value.isdigit() else "ERROR"
        
        case "ciudad":
            casted_value = check_ciudad(value)

        case "salario":
            casted_value = check_money_value(value)

        case "ruc":
            casted_value = check_ruc(value)


    """
    if isinstance(value, str):
        if is_date_format(value):
            casted_value = convert_to_sql_date_format(value)

        elif is_money_format(value):
            casted_value = convert_to_sql_decimal_format(value)
        
        elif field == "celular":
            casted_value = check_phone_number(value)

        elif field == "correo":
            casted_value = check_valid_mail_address(value)

        elif value.isdigit():
            casted_value = convert_to_int_if_possible(value, field)
        
        elif field == "cargas_familiares":
            casted_value = int(value) if value.isdigit() else ""
        
        elif field == "nombre_completo":
            casted_value = split_nombre_completo(value)

        elif field == "gender":
            casted_value = set_gender(value)
    """

    return casted_value
