import json
import urllib3
import requests
import mysql.connector
from mysql.connector import Error
from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from .controllers.customers_controllers import process_customers_page
from .controllers.operador_controllers import process_operador_page
from .controllers.campaigns_controllers import process_campaign_page
from .controllers.subcampaigns_controllers import subcampaigns_controllers
from .controllers.upload_bases_controllers import process_upload_customers_page
from .controllers.upload_leads_processes import process_upload_leads_page
from .controllers.Dinomi_controller import process_dinomi_page
from .controllers.FormularioController import process_formulario_page
from .controllers.Filter_controllers import process_filter_page
from .controllers.client_controllers import process_search_client_page
from .controllers.api_controller import process_api_request
from .forms.report_form import ReportForm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Check user access
def level_checker(nivel):
    def check_acces_level(user):
        group_permitted = ['OPERADOR', 'LIDER', 'SUPERVISOR', 'ADMIN']
        if nivel >= 2:
            group_permitted = group_permitted[nivel-1:]
        return user.groups.filter(name__in=group_permitted).exists()
    return check_acces_level

# auth
def login_view(req):
    if req.user.is_authenticated:
        grupos = req.user.groups.all()
        grupos = [grupo.name for grupo in grupos]
        if req.user.groups.filter(name="OPERADOR").exists():
            return redirect('/formularios/')
        if grupos and (grupos[0] in ['LIDER', 'SUPERVISOR', 'ADMIN']):
            return redirect('')
        logout_view(req)
    return LoginView.as_view(template_name='login.html')(req)

def logout_view(req):
    logout(req)
    return redirect('login')


def search_client(req):
    # Verificar si el usuario es administrador
    is_admin = req.user.groups.filter(name='ADMIN').exists()
    print("El usuario es administrador:", is_admin)
    context = {
        'is_admin': is_admin
    }
    return render(req, 'index.html', context)


@login_required
@user_passes_test(level_checker(3), login_url='/login/')
def home(req):
    return render(req, 'index.html')

# upload files
@login_required
@user_passes_test(level_checker(3))
def upload_users(req):
    return process_upload_customers_page(req)

@login_required
@user_passes_test(level_checker(3))
def upload_leads(req):
    return process_dinomi_page(req)

@login_required
@user_passes_test(level_checker(3))
def operadores(req):
    return process_operador_page(req)

@login_required
@user_passes_test(level_checker(3))
def edit_operador(req):
    return process_operador_page(req)

@login_required
@user_passes_test(level_checker(3))
def customers(req):
    return process_customers_page(req)

@login_required
@user_passes_test(level_checker(1), login_url='')
def formularios(req):
    return process_formulario_page(req)

@login_required
@user_passes_test(level_checker(1), login_url='')
def get_subcampanas(req):
    return process_formulario_page(req)

@login_required
@user_passes_test(level_checker(3))
def charts(req):
    return render(req, 'charts.html')

@login_required
@user_passes_test(level_checker(3))
def dashboard(req):
    return process_filter_page(req)

@login_required
@user_passes_test(level_checker(2))
def search_client(req):
    return process_search_client_page(req)

@login_required
@user_passes_test(level_checker(1))
def api(req):
    return process_api_request(req)

@login_required
@user_passes_test(level_checker(3))
def campaigns(req):
    return process_campaign_page(req)

# Nueva vista sub_campanhas
@login_required
@user_passes_test(level_checker(3))
def subcampanhas(req):
    # return render(req, 'sub_campanhas.html')
   return subcampaigns_controllers(req)


