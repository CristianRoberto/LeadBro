from ..AWS.RDS import connection
from ..forms.create_subcampaign_form import CreateSubCampaignForm
from django.shortcuts import render, redirect
from django.contrib import messages

# from django.contrib import messages
# from django.shortcuts import redirect

template_name = 'sub_campanhas.html'

def __get_subcampaigns(customerId=None):
    with connection() as conn:
        if customerId:
            query = (
                'SELECT s.id, s.nombre as Nombre_SubCampaña, c.nombre as Nombre_Campaña '
                'FROM subcampana s '
                'LEFT JOIN campana c ON s.id_campana = c.id '
                'WHERE s.id_campana = %s'
            )
            conn.execute(query, (customerId,))
        else:
            query = (
                'SELECT s.id, s.nombre as Nombre_SubCampaña, c.nombre as Nombre_Campaña '
                'FROM subcampana s '
                'LEFT JOIN campana c ON s.id_campana = c.id'
            )
            conn.execute(query)

        result = [i for i in conn]
    
    # Imprimir el resultado para depuración
    print("Resultado de la consulta de subcampañas:", result)
    
    return result

def __get_customers(id=None):
    with connection() as conn:
        if id:
            get_customers = 'SELECT id, nombre FROM subcampana WHERE id = %s'
            conn.execute(get_customers, (id,))
        else:
            conn.execute('SELECT id, nombre FROM compania')
        result = [i for i in conn]
    return result

def __check_GET_parameter(req):
    parameter = req.GET.get('subcampana')
    if parameter:
        try:
            parameter = int(parameter)
        except ValueError:
            parameter = None
    return parameter

# Obtener todas las campañas
# def __get_campaigns():
#     with connection() as conn:
#         query = 'SELECT id, nombre FROM campana'
#         conn.execute(query)
#         result = [i for i in conn]
#     return result


def __get_campaigns(campaign_id):
    with connection() as conn:
        query = 'SELECT id, nombre FROM campana WHERE id = %s'
        conn.execute(query, (campaign_id,))
        result = [i for i in conn]
    return result



def __get_customer_name(id):
    result = None
    if id:
        with connection() as conn:
            get_customer = (
                'SELECT nombre FROM subcampana '
                'WHERE id = %s'
            )
            conn.execute(get_customer, (id,))
            for i in conn:
                result = i
    if result:
        return result[0]
    return



def __create_new_campaign(request):
    data = request.POST
    name = data.get('name')
    listacampana = data.get('listacampana')

    if name and listacampana:
        add_campaign = (
            'INSERT INTO subcampana (nombre, id_campana) '
            'VALUES(%s, %s)'
        )

        values = (name, listacampana)

        query_is_successful = False
        with connection() as conn:
            conn.execute(add_campaign, values)
            if conn.rowcount:
                query_is_successful = True

        if query_is_successful:
            messages.success(request, 'Registro guardado correctamente.')
        else:
            messages.error(request, 'Error al guardar el registro.')
    else:
        messages.error(request, 'Datos insuficientes para crear la subcampaña.')

    return redirect('sub-campanhas') 




def __update_campaign(data):
    is_update = 'id' in data and data['id']  # Determinar si es actualización basada en la presencia de 'id'

    customers_list = [(data['customers'], data['name'])] if 'customers' in data else []
    campaigns_list = [(data['listacampana'], data['name'])]

    print(f"Subcampaign tuple: {customers_list}")
    print(f"Campaigns list: {campaigns_list}")

    form = CreateSubCampaignForm(data, customers_list=customers_list, campaigns_list=campaigns_list, is_update=is_update)
    if form.is_valid():
        update_campaign = (
            'UPDATE subcampana SET '
            'nombre = %s, '
            'id_campana = %s '
            'WHERE id = %s'
        )
        values = (
            form.cleaned_data['name'],
            form.cleaned_data['listacampana'],
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

def __checkPOST(request):
    if request.method == 'POST':
        body = request.POST
        if 'create_new_campaign' in body:
            result = __create_new_campaign(request)
            if result:
                return redirect(request.path)

        if 'update-campaign-data' in body:
            result = __update_campaign(body)
            if result:
                return redirect(request.path)
            
def __set_context(req):
    customer = __check_GET_parameter(req)
    subcampaigns = __get_subcampaigns(customer)
    customer_choices = __get_customers(customer)

    # Imprimir los valores de customer_choices en la consola del servidor
    print("Customer Choices:", customer_choices)

    # Obtener el ID de la primera opción de customer_choices
    if customer_choices:
        campaign_id = customer_choices[0][0]
    else:
        campaign_id = 1  # El ID de la campaña por defecto

    campaign_choices = __get_campaigns(campaign_id)
    form = CreateSubCampaignForm(customers_list=customer_choices, campaigns_list=campaign_choices)
    customer_name = __get_customer_name(customer)
    campaign_info = __zip_campaigns_and_forms(subcampaigns)

    context = {
        'subcampaigns': subcampaigns,
        'form': form,
        'customer_name': customer_name,
        'campaign_info': campaign_info,
        'customer_choices': customer_choices,  # Añadir esto al contexto
        'campaign_id': campaign_id  # Añadir el campaign_id al contexto
    }
    return context

def __zip_campaigns_and_forms(subcampaigns):
    CAMPAIGN_ID = 0
    SUBCAMPAIGN_NAME = 1
    CAMPAIGN_NAME = 2

    campaigns_to_edit = [
        CreateSubCampaignForm(
            initial={
                'name': subcampaign[SUBCAMPAIGN_NAME],
                'listacampana': subcampaign[CAMPAIGN_ID],
                'id': subcampaign[0]
            },
            customers_list=[(subcampaign[CAMPAIGN_ID], subcampaign[CAMPAIGN_NAME])],
            campaigns_list=[(subcampaign[CAMPAIGN_ID], subcampaign[CAMPAIGN_NAME])],
            is_update=True
        )
        for subcampaign in subcampaigns
    ]
    campaign_info = zip(subcampaigns, campaigns_to_edit)

    return campaign_info




# def __checkPOST(request):
#     if request.method == 'POST':
#         body = request.POST
#         if 'create_new_campaign' in body:
#             result = __create_new_campaign(request)
#             if result:
#                 return redirect(request.path)


                

def subcampaigns_controllers(req):
    post = __checkPOST(req)
    if post:
        return post

    context = __set_context(req)
    return render(req, template_name, context)
