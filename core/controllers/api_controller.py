from django.http import Http404, HttpResponse, JsonResponse
from ..AWS.RDS import connection

from django.shortcuts import render, redirect
from mysql.connector import IntegrityError
from datetime import datetime


def __getSubcamapanas(campana):
    query = (
        "SELECT subcamp.id, "
        "    subcamp.nombre "
        "FROM subcampana subcamp "
        "JOIN campana camp ON camp.id = subcamp.id_campana "
        "WHERE camp.id = %s "
    )

    with connection() as conn:
        conn.execute(query, (campana,))
        subcampanas = conn.fetchall()

    listSubcampanas = []
    if len(subcampanas) > 0:
        listSubcampanas = [{'id': row[0], 'nombre': row[1]} for row in subcampanas]    
    return JsonResponse(listSubcampanas, safe=False)

def __getCampanas(compania_id):
    query = (
        "SELECT camp.id, "
        "    camp.nombre "
        "FROM campana camp "
        "JOIN compania com ON com.id = camp.id_compania "
        "WHERE camp.id_compania = %s "
    )

    with connection() as conn:
        conn.execute(query, (compania_id,))
        campanas = conn.fetchall()

    listCampanas = []
    if len(campanas) > 0:
        listCampanas = [{'id': row[0], 'nombre': row[1]} for row in campanas]    
    return JsonResponse(listCampanas, safe=False)


def __checkProfile(req):
    grupos = req.user.groups.all()    
    grupos = [grupo.name for grupo in grupos]

    return grupos[0] in ["OPERADOR", "SUPERVISOR", "LIDER", "ADMIN"]
        


def __checkRequirements(req):
    if req.method == "GET":
        if not __checkProfile(req): return

        params = req.GET

        if "campana" in params:
            campana_id = params.get("campana")
            if not campana_id:
                raise Http404("ID de la campaña no proporcionado")
            
            return __getSubcamapanas(campana_id)

        if "compania" in params:
            compania_id = params.get("compania")
            if not compania_id:
                raise Http404("ID de la compañia no proporcionado")
            
            return __getCampanas(compania_id)

        return


def process_api_request(req):

    result = __checkRequirements(req)

    if not result:
        result = JsonResponse({"data": "no data"}, safe=False)

    return result