from ..AWS.RDS import connection
from ..forms.create_customer_form import create_customer_form

from django.shortcuts import render, redirect
from mysql.connector import IntegrityError

template_name = 'customers.html'

def __get_customers():
    query = 'SELECT * FROM compania'
    with connection() as conn:
        conn.execute(query)
        result = [i for i in conn]
    return result


def __create_new_customer(data):
    form = create_customer_form(data)
    if form.is_valid():
        add_customer = (
            'INSERT INTO compania '
            '(nombre, nombre_contacto, telefono_contacto, correo_contacto) '
            'VALUES (%s, %s, %s, %s)'
        )

        values = (
            form.cleaned_data['name'],
            form.cleaned_data['contact_name'],
            form.cleaned_data['contact_phone'],
            form.cleaned_data['contact_email']
        )

        query_is_successfull = False
        with connection() as conn:
            conn.execute(add_customer, values)
            if conn.rowcount:
                query_is_successfull = True

        return query_is_successfull

    else:
        print(form.errors)
    return


def __update_customer(data):
    form = create_customer_form(data)
    if form.is_valid():
        update_customer = (
            'UPDATE compania SET '
            'nombre = %s, '
            'nombre_contacto = %s, '
            'telefono_contacto = %s, '
            'correo_contacto = %s '
            'WHERE id = %s'
        )

        values = (
            form.cleaned_data['name'],
            form.cleaned_data['contact_name'],
            form.cleaned_data['contact_phone'],
            form.cleaned_data['contact_email'],
            form.cleaned_data['id']
        )

        query_is_successfull = False
        with connection() as conn:
            conn.execute(update_customer, values)
            if conn.rowcount:
                query_is_successfull = True

        return query_is_successfull

    else:
        print(form.errors)
    return


def __delete_customer(req):
    id = req.POST['id']
    delete_customer = 'DELETE FROM compania WHERE id = %s' % id

    context = __set_context()

    
    with connection() as conn:
        try:
            conn.execute(delete_customer)
            if conn.rowcount:
                return redirect(req.path)
        except IntegrityError:
            context = __set_context()
            err_msg = 'No se pude borrar la compañía debido a que hay leads o clientes que dependen de esta compañía'
            context.update({'query_error': err_msg})
            return render(req, template_name, context)

    return render(req, template_name, context)


    

def __zip_customers_and_forms(customers):
    customers_to_edit = [create_customer_form(initial={
        'name': customer[1],
        'contact_name': customer[2],
        'contact_phone': customer[3],
        'contact_email': customer[4],
        'id': customer[0]
    }) for customer in customers]

    customers_info = zip(customers, customers_to_edit)

    return customers_info


def __checkPOST(req):
    if req.method == 'POST':
        body = req.POST

        if 'create_new_customer' in body:
            result = __create_new_customer(body)
            if result:
                return redirect(req.path)

        if 'update-customer-data' in body:
            result = __update_customer(body)
            if result:
                return redirect(req.path)

        if 'delete-customer' in body:
            result = __delete_customer(req)
            if result:
                return result


def __set_context():
    customers = __get_customers()
    customers_info = __zip_customers_and_forms(customers)

    context = {
        'customers': customers,
        'create_customer_form': create_customer_form,
        'customers_info': customers_info
    }

    return context


def process_customers_page(req):
    post = __checkPOST(req)

    if post:
        return post

    context = __set_context()

    return render(req, template_name, context)
