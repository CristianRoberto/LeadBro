from django import template

register = template.Library()

@register.simple_tag
def get_field(form, field, id):
    try:
        field_name = f"{field}{id}"
        return form[field_name]
    except KeyError:
        return ''  # Devuelve una cadena vacía si el campo no existe