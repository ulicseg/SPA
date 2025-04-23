from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Perfil
from GestorSpa.apps.turnos.models import Turno
from GestorSpa.apps.servicios.models import Servicio

# Create your views here.

@login_required
def perfil(request):
    # Obtener estadísticas
    turnos_count = Turno.objects.count()
    servicios_count = Servicio.objects.count()

    # Obtener los últimos 5 turnos
    ultimos_turnos = Turno.objects.all().order_by('-fecha', '-hora_inicio')[:5]

    # Crear perfil si no existe
    if not hasattr(request.user, 'perfil'):
        Perfil.objects.create(usuario=request.user)

    context = {
        'turnos_count': turnos_count,
        'servicios_count': servicios_count,
        'ultimos_turnos': ultimos_turnos,
    }
    return render(request, 'perfil.html', context)

@login_required
def perfil_edit(request):
    # Asegurarse de que existe el perfil
    if not hasattr(request.user, 'perfil'):
        Perfil.objects.create(usuario=request.user)
    
    if request.method == 'POST':
        # Actualizar datos del usuario
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Actualizar datos del perfil
        perfil = request.user.perfil
        perfil.telefono = request.POST.get('telefono', '')
        perfil.direccion = request.POST.get('direccion', '')
        perfil.bio = request.POST.get('bio', '')
        
        # Manejar la foto de perfil
        if 'foto' in request.FILES:
            perfil.foto = request.FILES['foto']
        
        # Manejar la fecha de nacimiento
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        if fecha_nacimiento:
            perfil.fecha_nacimiento = fecha_nacimiento
        
        perfil.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('usuarios:perfil')
    
    return render(request, 'perfil_edit.html', {'user': request.user})
