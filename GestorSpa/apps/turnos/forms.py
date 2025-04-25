from django import forms
from .models import Turno
from django.core.exceptions import ValidationError
from django.utils import timezone

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['nombre', 'email', 'telefono', 'servicio', 'fecha', 'hora_inicio', 'notas']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+54 9 11 1234-5678'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ejemplo@email.com'}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

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