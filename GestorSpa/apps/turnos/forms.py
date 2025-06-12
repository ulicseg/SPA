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
                self.fields['profesional'].queryset = servicio.profesional_set.filter(estado='activo')
            except (ValueError, Servicio.DoesNotExist):
                self.fields['profesional'].queryset = Profesional.objects.none()
        elif self.instance.pk and self.instance.servicio:
            self.fields['profesional'].queryset = self.instance.servicio.profesional_set.filter(estado='activo')
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

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        servicio = cleaned_data.get('servicio')

        if fecha and hora_inicio and servicio:
            # Verificar si ya existe un turno en el mismo horario
            turnos_existentes = Turno.objects.filter(
                fecha=fecha,
                hora_inicio=hora_inicio,
                servicio=servicio
            )
            
            # Excluir el turno actual en caso de edición
            if self.instance.pk:
                turnos_existentes = turnos_existentes.exclude(pk=self.instance.pk)
            
            if turnos_existentes.exists():
                raise ValidationError('Ya existe un turno agendado para esta fecha y hora.')

        return cleaned_data

    def get_horarios_disponibles(self, fecha, servicio, profesional):
        from datetime import datetime, timedelta, time
        # Obtener horario del profesional para ese día
        dia = fecha.strftime('%A').lower()
        inicio_prof = getattr(profesional, f"hora_inicio_{dia}")
        fin_prof = getattr(profesional, f"hora_fin_{dia}")
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