from django.shortcuts import render
from GestorSpa.apps.servicios.models import Servicio

def home(request):
    try:
        servicios = Servicio.objects.filter(activo=True)
    except:
        servicios = []
    return render(request, 'index.html', {'servicios': servicios}) 