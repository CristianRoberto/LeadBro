from ..AWS.RDS import connection
from ..forms.create_campaign_form import create_campaign_form

from django.shortcuts import render, redirect
from mysql.connector import IntegrityError
from django.contrib import messages



template_name = 'campaigns.html'


def __get_campaigns(customerId=None):
    with connection() as conn:
        if customerId:
            get_campaigns = (
                'SELECT campana.*, compania.nombre '
                'FROM campana '
                'JOIN compania ON campana.id_compania = compania.id '
                'WHERE campana.id_compania = %s'
            )
            conn.execute(get_campaigns, (customerId,))

        else:
            get_campaigns = (
                'SELECT campana.*, compania.nombre '
                'FROM campana '
                'JOIN compania ON campana.id_compania = compania.id '
            )
            conn.execute(get_campaigns)

        result = [i for i in conn]

    return result


def __get_customers(id=None):
    with connection() as conn:
        if id:
            get_customers = (
                'SELECT id, nombre FROM compania '
                'WHERE id = %s'
            )
            conn.execute(get_customers, (id,))

        else:
            conn.execute('SELECT id, nombre FROM compania')

        result = [i for i in conn]

    return result


def __check_GET_parameter(req):
    parameter = req.GET.get('compania')
    if parameter:
        try:
            parameter = int(parameter)
        except ValueError:
            parameter = None

    return parameter


def __get_customer_name(id):
    result = None
    if id:
        with connection() as conn:
            get_customer = (
                'SELECT nombre FROM compania '
                'WHERE id = %s'
            )

            conn.execute(get_customer, (id,))
            for i in conn:
                result = i

    if result:
        return result[0]
    return

def __create_new_campaign(request, data):
    customers_list = [
        (data.get('customers'), data.get('name'))
    ]
    form = create_campaign_form(data, customers_list=customers_list)
    if form.is_valid():
        add_campaign = (
            'INSERT INTO campana '
            '(nombre, id_compania) '
            'VALUES(%s, %s)'
        )

        values = (
            form.cleaned_data['name'],
            form.cleaned_data['customers']
        )

        query_is_successful = False
        with connection() as conn:
            conn.execute(add_campaign, values)
            if conn.rowcount:
                query_is_successful = True

        if query_is_successful:
            messages.success(request, 'Registro guardado correctamente.')
        else:
            messages.error(request, 'Error al guardar el registro.')

        return query_is_successful

    else:
        print("Error de validación del formulario:", form.errors)
        return False





def __delete_campaign(req):
    id = req.POST['id']
    delete_campaign = 'DELETE FROM campana WHERE id = %s' % id

    query_is_successful = False
    with connection() as conn:
        try:
            print("Antes de ejecutar la consulta de eliminación")
            conn.execute(delete_campaign)
            print("Después de ejecutar la consulta de eliminación")
            if conn.rowcount:
                query_is_successful = True
        except IntegrityError:
            context = __set_context(req)
            err_msg = 'No se puede borrar la campaña debido a que hay leads o clientes que dependen de esta campaña'
            context.update({'query_error': err_msg})
            return render(req, template_name, context)
        except Exception as e:
            print("Se produjo un error:", str(e))  # Imprimir el mensaje de error
            raise e  # Relanzar la excepción para obtener más información

    return query_is_successful



def __update_campaign(data):
    customers_list = [(
        data['customers'],
        data['name']
    )]
    form = create_campaign_form(data, customers_list=customers_list)
    if form.is_valid():
        update_campaign = (
            'UPDATE campana SET '
            'nombre = %s, '
            'id_compania = %s '
            'WHERE id = %s'
        )
        values = (
            form.cleaned_data['name'],
            form.cleaned_data['customers'],
            form.cleaned_data['id']
        )

        query_is_successfull = False
        with connection() as conn:
            conn.execute(update_campaign, values)
            if conn.rowcount:
                query_is_successfull = True

        return query_is_successfull

    else:
        print(form.errors)
    return


def __zip_campaigns_and_forms(campaigns):
    CUSTOMER_ID = 2
    CUSTOMER_NAME = 3

    campaigns_to_edit = [
        create_campaign_form(
            initial={
                'name': campaign[1],
                'id': campaign[0]
            },
            customers_list=[(campaign[CUSTOMER_ID], campaign[CUSTOMER_NAME])]
        )
        for campaign in campaigns
    ]
    campaign_info = zip(campaigns, campaigns_to_edit)

    return campaign_info




def __set_context(req):
    customer = __check_GET_parameter(req)
    campaigns = __get_campaigns(customer)
    customer_choices = __get_customers(customer)
    form = create_campaign_form(customers_list=customer_choices)
    customer_name = __get_customer_name(customer)
    campaign_info = __zip_campaigns_and_forms(campaigns)

    context = {
        'campaigns': campaigns,
        'form': form,
        'customer_name': customer_name,
        'campaign_info': campaign_info
    }

    return context


def __checkPOST(request):
    if request.method == 'POST':
        body = request.POST

        if 'create_new_campaign' in body:
            result = __create_new_campaign(request, body)
            if result:
                return redirect(request.path)

        # El resto de tu código...


        if 'delete-campaign' in body:
            result = __delete_campaign(request)
            if result:
                return result

        if 'update-campaign-data' in body:
            result = __update_campaign(body)
            if result:
                return redirect(request.path)




def process_campaign_page(req):
    post = __checkPOST(req)

    if post:
        return post

    context = __set_context(req)

    return render(req, template_name, context)