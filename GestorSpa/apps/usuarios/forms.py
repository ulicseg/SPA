from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Perfil, Profesional


class PerfilForm(forms.ModelForm):
    """Formulario para editar el perfil básico del usuario"""
    
    class Meta:
        model = Perfil
        fields = ['telefono', 'direccion', 'foto', 'bio', 'fecha_nacimiento']
        widgets = {
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: +54 9 11 1234-5678'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Cuéntanos un poco sobre ti...'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class ProfesionalForm(forms.ModelForm):
    """Formulario para que los profesionales editen su información específica"""
    
    # Campos adicionales para información del usuario
    first_name = forms.CharField(
        label='Nombre',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    # Campo para días disponibles como checkboxes
    DIAS_CHOICES = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]
    
    dias_trabajo = forms.MultipleChoiceField(
        choices=DIAS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Días de Trabajo',
        required=False
    )
    
    class Meta:
        model = Profesional
        fields = [
            'nombre_completo', 'especialidad', 'telefono', 'email_profesional',
            'numero_licencia', 'años_experiencia', 'certificaciones',
            'hora_inicio_disponibilidad', 'hora_fin_disponibilidad',
            'biografia', 'foto_profesional', 'servicios_que_ofrece'
        ]
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del profesional'
            }),
            'especialidad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'email_profesional': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@ejemplo.com'
            }),
            'numero_licencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de licencia profesional'
            }),
            'años_experiencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50
            }),
            'certificaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Lista tus certificaciones, cursos y especializaciones...'
            }),
            'hora_inicio_disponibilidad': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'hora_fin_disponibilidad': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'biografia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe tu experiencia profesional, métodos de trabajo y filosofía...'
            }),
            'foto_profesional': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'servicios_que_ofrece': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nombre_completo': 'Nombre Completo',
            'especialidad': 'Especialidad Principal',
            'telefono': 'Teléfono',
            'email_profesional': 'Email Profesional',
            'numero_licencia': 'Número de Licencia',
            'años_experiencia': 'Años de Experiencia',
            'certificaciones': 'Certificaciones y Cursos',
            'hora_inicio_disponibilidad': 'Hora de Inicio',
            'hora_fin_disponibilidad': 'Hora de Fin',
            'biografia': 'Biografía Profesional',
            'foto_profesional': 'Foto Profesional',
            'servicios_que_ofrece': 'Servicios que Ofreces',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-llenar datos del usuario
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
        
        # Pre-llenar días disponibles si existe la instancia
        if self.instance and self.instance.pk:
            dias_disponibles = self.instance.get_dias_disponibles_list()
            self.fields['dias_trabajo'].initial = dias_disponibles
    
    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio_disponibilidad')
        hora_fin = cleaned_data.get('hora_fin_disponibilidad')
        
        # Validar que la hora de fin sea mayor que la de inicio
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise ValidationError(
                'La hora de fin debe ser posterior a la hora de inicio.'
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        profesional = super().save(commit=False)
        
        # Actualizar información del usuario
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            if commit:
                self.user.save()
        
        # Procesar días de trabajo
        dias_seleccionados = self.cleaned_data.get('dias_trabajo', [])
        profesional.dias_disponibles = ','.join(dias_seleccionados)
        
        if commit:
            profesional.save()
            self.save_m2m()  # Guardar relaciones many-to-many
        
        return profesional


class UserProfesionalForm(forms.ModelForm):
    """Formulario para datos básicos del usuario profesional"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@ejemplo.com'
            }),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Email',
        }
