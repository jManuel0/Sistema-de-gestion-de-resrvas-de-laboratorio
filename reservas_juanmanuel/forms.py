from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import Reserva


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['laboratorio', 'fecha', 'hora_inicio', 'hora_fin', 'motivo']
        widgets = {
            'laboratorio': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'laboratorio': 'Laboratorio',
            'fecha': 'Fecha',
            'hora_inicio': 'Hora de inicio',
            'hora_fin': 'Hora de fin',
            'motivo': 'Motivo',
        }

    def clean(self):
        cleaned_data = super().clean()
        laboratorio = cleaned_data.get('laboratorio')
        fecha = cleaned_data.get('fecha')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')

        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            self.add_error('hora_fin', 'La hora de fin debe ser mayor que la hora de inicio.')

        if laboratorio and fecha and hora_inicio and hora_fin:
            reservas_cruzadas = Reserva.objects.filter(
                laboratorio__iexact=laboratorio.strip(),
                fecha=fecha,
            ).filter(Q(hora_inicio__lt=hora_fin) & Q(hora_fin__gt=hora_inicio))

            if self.instance.pk:
                reservas_cruzadas = reservas_cruzadas.exclude(pk=self.instance.pk)

            if reservas_cruzadas.exists():
                raise ValidationError(
                    'Ya existe una reserva en ese laboratorio que se cruza con el horario seleccionado.'
                )

        return cleaned_data


class RegistroUsuarioForm(UserCreationForm):
    ROL_CHOICES = [
        ('Docente', 'Docente'),
        ('Administrador', 'Administrador'),
    ]

    email = forms.EmailField(required=False)
    rol = forms.ChoiceField(choices=ROL_CHOICES, label='Rol')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'rol', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
