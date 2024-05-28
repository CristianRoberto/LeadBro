from django.urls import path
from django.contrib.auth.views import LoginView

from . import views

urlpatterns = [
    path('', views.home, name=''),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('subir-leads/', views.upload_leads, name='subir-leads'),
    path('subir-clientes/', views.upload_users, name='subir-clientes'),
    path('companias/', views.customers , name='companias'),
    path('operadores/', views.operadores , name='operadores'),
    path('operadores/edit/', views.edit_operador, name='edit-operador'),
    path('api/', views.api , name='api'),
    path('formularios/', views.formularios , name='formularios'),
    path('formularios/subcampanas/', views.get_subcampanas , name='get_subcampanas'),
    path('reportes/', views.charts, name='reportes'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search-client/', views.search_client, name='search-client'),

    path('campanhas/', views.campaigns, name='campanhas'),
    path('sub-campanhas/', views.subcampanhas, name='sub-campanhas'),  # Asegúrate de tener esto si lo usas en el template

]
