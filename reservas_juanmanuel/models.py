from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Reserva(models.Model):
    class Estados(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADA = 'aprobada', 'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservas'
    )
    laboratorio = models.CharField(max_length=100)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(
        max_length=20, choices=Estados.choices, default=Estados.PENDIENTE
    )
    motivo = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha', 'hora_inicio', 'laboratorio']
        indexes = [
            models.Index(fields=['laboratorio', 'fecha', 'hora_inicio', 'hora_fin']),
            models.Index(fields=['estado']),
        ]

    def __str__(self) -> str:
        return f'{self.laboratorio} - {self.fecha} {self.hora_inicio}-{self.hora_fin} ({self.get_estado_display()})'

    def clean(self) -> None:
        super().clean()

        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError({'hora_fin': 'La hora de fin debe ser posterior a la hora de inicio.'})

        if not (self.laboratorio and self.fecha and self.hora_inicio and self.hora_fin):
            return

        # Conflicto si se solapa: inicio < fin_existente AND fin > inicio_existente
        conflicto_qs = (
            Reserva.objects.filter(laboratorio__iexact=self.laboratorio.strip(), fecha=self.fecha)
            .filter(Q(hora_inicio__lt=self.hora_fin) & Q(hora_fin__gt=self.hora_inicio))
        )
        if self.pk:
            conflicto_qs = conflicto_qs.exclude(pk=self.pk)

        if conflicto_qs.exists():
            raise ValidationError('Ya existe una reserva que se cruza con ese horario en el mismo laboratorio.')

    def save(self, *args, **kwargs):
        # Garantiza que se apliquen validaciones del modelo en el CRUD.
        self.full_clean()
        return super().save(*args, **kwargs)
