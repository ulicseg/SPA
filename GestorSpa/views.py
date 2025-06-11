from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from GestorSpa.apps.servicios.models import Servicio

def home(request):
    # Si el usuario está autenticado, redirigir a su dashboard específico
    if request.user.is_authenticated:
        try:
            # Verificar si el usuario tiene perfil y rol
            if hasattr(request.user, 'perfil') and request.user.perfil.rol:
                # Redirigir al dashboard según el rol
                return redirect('usuarios:dashboard_rol')
        except:
            pass  # Si hay algún error, continuar con la vista normal
    
    # Para usuarios no autenticados o en caso de error, mostrar página principal
    try:
        servicios = Servicio.objects.filter(activo=True)[:6]  # Limitar a 6 servicios para la página principal
    except:
        servicios = []
    
    context = {
        'servicios': servicios,
        'is_home_page': True
    }
    return render(request, 'index.html', context)