from django import forms
from .models import Turno
from django.core.exceptions import ValidationError
from django.utils import timezone
from GestorSpa.apps.usuarios.models import Profesional
from GestorSpa.apps.servicios.models import Servicio

class TurnoForm(forms.ModelForm):
    profesional = forms.ModelChoiceField(
        queryset=Profesional.objects.none(),
        required=True,
        label="Profesional",
        help_text="Solo se muestran profesionales habilitados para el servicio y con disponibilidad."
    )
    hora_inicio = forms.ChoiceField(
        choices=[],
        required=True,
        label="Hora de inicio"
    )
    
    class Meta:
        model = Turno
        fields = ['nombre', 'email', 'telefono', 'servicio', 'profesional', 'fecha', 'hora_inicio', 'notas', 'metodo_pago', 'pagado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+54 9 11 1234-5678'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ejemplo@email.com'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'servicio' in self.data:
            try:
                servicio_id = int(self.data.get('servicio'))
                servicio = Servicio.objects.get(pk=servicio_id)
                # Obtener profesionales que tienen este servicio en sus especialidades
                self.fields['profesional'].queryset = Profesional.objects.filter(
                    servicios_especialidad=servicio,
                    estado='activo'
                )
            except (ValueError, Servicio.DoesNotExist):
                self.fields['profesional'].queryset = Profesional.objects.none()
        elif self.instance.pk and self.instance.servicio:
            # Obtener profesionales que tienen este servicio en sus especialidades
            self.fields['profesional'].queryset = Profesional.objects.filter(
                servicios_especialidad=self.instance.servicio,
                estado='activo'
            )
        else:
            self.fields['profesional'].queryset = Profesional.objects.filter(estado='activo')
        
        # Horarios disponibles
        if 'fecha' in self.data and 'servicio' in self.data and 'profesional' in self.data:
            try:
                servicio = Servicio.objects.get(pk=int(self.data.get('servicio')))
                profesional = Profesional.objects.get(pk=int(self.data.get('profesional')))
                fecha = self.data.get('fecha')
                from datetime import datetime
                fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
                horarios = self.get_horarios_disponibles(fecha_dt, servicio, profesional)
                self.fields['hora_inicio'].choices = [(h, h) for h in horarios]
            except Exception:
                self.fields['hora_inicio'].choices = []
        elif self.instance.pk:
            self.fields['hora_inicio'].choices = [(self.instance.hora_inicio.strftime('%H:%M'), self.instance.hora_inicio.strftime('%H:%M'))]
        else:
            self.fields['hora_inicio'].choices = []

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha:
            if fecha < timezone.now().date():
                raise ValidationError('No se pueden agendar turnos en fechas pasadas.')
        return fecha

    def clean_hora_inicio(self):
        """Convierte la hora de string a objeto time"""
        hora_inicio = self.cleaned_data.get('hora_inicio')
        if hora_inicio:
            try:
                from datetime import datetime
                # Si es string, convertir a time
                if isinstance(hora_inicio, str):
                    return datetime.strptime(hora_inicio, '%H:%M').time()
                # Si ya es time, devolver tal como está
                elif hasattr(hora_inicio, 'hour'):
                    return hora_inicio
                else:                    raise ValidationError('Formato de hora inválido.')
            except ValueError:
                raise ValidationError('Formato de hora inválido. Use HH:MM')
        return hora_inicio

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        servicio = cleaned_data.get('servicio')
        profesional = cleaned_data.get('profesional')
        email = cleaned_data.get('email')

        if fecha and hora_inicio and profesional:
            # Convertir hora_inicio a objeto time si es string
            if isinstance(hora_inicio, str):
                from datetime import datetime
                try:
                    hora_inicio = datetime.strptime(hora_inicio, '%H:%M').time()
                except ValueError:
                    raise ValidationError('Formato de hora inválido.')

            # 1. Verificar si el profesional ya tiene un turno en ese horario
            turnos_profesional = Turno.objects.filter(
                fecha=fecha,
                hora_inicio=hora_inicio,
                profesional=profesional
            ).exclude(estado='cancelado')
            
            # Excluir el turno actual en caso de edición
            if self.instance.pk:
                turnos_profesional = turnos_profesional.exclude(pk=self.instance.pk)
            
            if turnos_profesional.exists():
                raise ValidationError(
                    f'El profesional {profesional.nombre_completo} ya tiene un turno agendado '
                    f'para el {fecha.strftime("%d/%m/%Y")} a las {hora_inicio.strftime("%H:%M")}.'
                )

            # 2. Verificar si el cliente ya tiene un turno con el mismo profesional en ese horario
            if email:
                turnos_cliente = Turno.objects.filter(
                    fecha=fecha,
                    hora_inicio=hora_inicio,
                    profesional=profesional,
                    email=email
                ).exclude(estado='cancelado')
                
                # Excluir el turno actual en caso de edición
                if self.instance.pk:
                    turnos_cliente = turnos_cliente.exclude(pk=self.instance.pk)
                
                if turnos_cliente.exists():
                    raise ValidationError(
                        f'Ya tienes un turno agendado con {profesional.nombre_completo} '
                        f'para el {fecha.strftime("%d/%m/%Y")} a las {hora_inicio.strftime("%H:%M")}.'
                    )

        return cleaned_data

    def get_horarios_disponibles(self, fecha, servicio, profesional):
        from datetime import datetime, timedelta, time
        import locale
        
        # Obtener día de la semana en inglés para evitar problemas de locale
        try:
            # Guardar locale actual
            current_locale = locale.getlocale()
            # Cambiar temporalmente a inglés
            locale.setlocale(locale.LC_TIME, 'C')
            dia = fecha.strftime('%A').lower()
            # Restaurar locale
            locale.setlocale(locale.LC_TIME, current_locale)
        except:
            # Si no se puede cambiar el locale, usar el mapeo manual
            weekday = fecha.weekday()  # 0=Monday, 1=Tuesday, etc.
            dias_ingles = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            dia = dias_ingles[weekday]
        
        # Convertir días en inglés a español
        dias_conversion = {
            'monday': 'lunes',
            'tuesday': 'martes', 
            'wednesday': 'miercoles',
            'thursday': 'jueves',
            'friday': 'viernes',
            'saturday': 'sabado',
            'sunday': 'domingo'
        }
        dia_es = dias_conversion.get(dia, dia)
        
        inicio_prof = getattr(profesional, f"hora_inicio_{dia_es}", None)
        fin_prof = getattr(profesional, f"hora_fin_{dia_es}", None)
        
        if not inicio_prof or not fin_prof:
            return []
        
        # Generar slots según duración del servicio
        hora_actual = datetime.combine(fecha, inicio_prof)
        hora_fin = datetime.combine(fecha, fin_prof)
        horarios = []
        
        while hora_actual + timedelta(minutes=servicio.duracion) <= hora_fin:
            # Verificar superposición
            solapados = Turno.objects.filter(
                profesional=profesional,
                fecha=fecha,
                estado__in=['pendiente', 'confirmado'],
                hora_inicio__lt=(hora_actual + timedelta(minutes=servicio.duracion)).time(),
                hora_fin__gt=hora_actual.time()
            )
            if not solapados.exists():
                horarios.append(hora_actual.strftime('%H:%M'))
            hora_actual += timedelta(minutes=servicio.intervalo)
        
        return horarios
