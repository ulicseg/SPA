from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
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
                'placeholder': 'Ej: +54 11 1234-5678'
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
                'placeholder': 'Cuéntanos sobre ti...'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class UsuarioForm(forms.ModelForm):
    """Formulario para editar información básica del usuario"""
    
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
                'placeholder': 'correo@ejemplo.com'
            }),
        }


class ProfesionalForm(forms.ModelForm):
    """Formulario para editar información profesional completa"""
    servicios_especialidad = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': 8,
        }),
        label="Servicios que puede realizar",
        help_text="Seleccione los servicios para los que está capacitado."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from GestorSpa.apps.servicios.models import Servicio
        self.fields['servicios_especialidad'].queryset = Servicio.objects.filter(activo=True)
        if self.instance.pk:
            self.fields['servicios_especialidad'].initial = self.instance.servicios_especialidad.all()

    class Meta:
        model = Profesional
        fields = [
            'nombre_completo', 'especialidad', 'especialidades_secundarias',
            'contacto', 'telefono_profesional', 'numero_matricula', 
            'colegio_profesional', 'biografia', 'experiencia_anos',
            'foto_profesional', 'disponibilidad_notas', 'servicios_especialidad'
        ]
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo profesional'
            }),
            'especialidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Masajes Terapéuticos'
            }),
            'especialidades_secundarias': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Otras especialidades separadas por comas'
            }),
            'contacto': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email profesional'
            }),
            'telefono_profesional': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto profesional'
            }),
            'numero_matricula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de matrícula profesional'
            }),
            'colegio_profesional': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Colegio o asociación profesional'
            }),
            'biografia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Información sobre tu experiencia, formación y filosofía profesional...'
            }),
            'experiencia_anos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50
            }),
            'foto_profesional': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'disponibilidad_notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Información adicional sobre horarios y disponibilidad'
            }),
        }
    
    def clean_numero_matricula(self):
        numero_matricula = self.cleaned_data.get('numero_matricula')
        if numero_matricula:
            # Verificar que no exista otro profesional con la misma matrícula
            qs = Profesional.objects.filter(numero_matricula=numero_matricula)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise ValidationError('Ya existe un profesional con este número de matrícula.')
        
        return numero_matricula


class HorariosProfesionalForm(forms.ModelForm):
    """Formulario específico para gestionar horarios de disponibilidad"""
    
    class Meta:
        model = Profesional
        fields = [
            'hora_inicio_lunes', 'hora_fin_lunes',
            'hora_inicio_martes', 'hora_fin_martes',
            'hora_inicio_miercoles', 'hora_fin_miercoles',
            'hora_inicio_jueves', 'hora_fin_jueves',
            'hora_inicio_viernes', 'hora_fin_viernes',
            'hora_inicio_sabado', 'hora_fin_sabado',
            'hora_inicio_domingo', 'hora_fin_domingo',
        ]
        widgets = {
            'hora_inicio_lunes': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin_lunes': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_inicio_martes': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin_martes': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_inicio_miercoles': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin_miercoles': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_inicio_jueves': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin_jueves': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_inicio_viernes': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin_viernes': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_inicio_sabado': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin_sabado': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_inicio_domingo': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin_domingo': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que las horas de fin sean posteriores a las de inicio
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        
        for dia in dias:
            inicio_field = f'hora_inicio_{dia}'
            fin_field = f'hora_fin_{dia}'
            
            hora_inicio = cleaned_data.get(inicio_field)
            hora_fin = cleaned_data.get(fin_field)
            
            if hora_inicio and hora_fin:
                if hora_inicio >= hora_fin:
                    raise ValidationError(
                        f'La hora de fin del {dia.capitalize()} debe ser posterior a la hora de inicio.'
                    )
            elif hora_inicio and not hora_fin:
                raise ValidationError(
                    f'Debe especificar la hora de fin para el {dia.capitalize()}.'
                )
            elif not hora_inicio and hora_fin:
                raise ValidationError(
                    f'Debe especificar la hora de inicio para el {dia.capitalize()}.'
                )
        
        return cleaned_data


class EstadoProfesionalForm(forms.ModelForm):
    """Formulario para cambiar el estado del profesional"""
    
    class Meta:
        model = Profesional
        fields = ['estado', 'fecha_inicio', 'fecha_fin', 'observaciones']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observaciones internas...'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            if fecha_inicio >= fecha_fin:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
        
        return cleaned_data


class ClienteRegistroForm(UserCreationForm):
    """Formulario de registro para nuevos clientes"""
    
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu apellido'
        })
    )
    
    email = forms.EmailField(
        required=True,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
    )
    
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label='Teléfono (opcional)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+54 11 1234-5678'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario (único)'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar widgets para contraseñas
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña'
        })
          # Personalizar labels
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este correo electrónico.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # El perfil se crea automáticamente por el signal, solo lo actualizamos
            perfil = user.perfil
            perfil.telefono = self.cleaned_data.get('telefono', '')
            perfil.tipo_usuario = 'cliente'
            perfil.save()
        return user
