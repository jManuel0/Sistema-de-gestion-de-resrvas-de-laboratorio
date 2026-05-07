from django.contrib import admin

from .models import Reserva


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('laboratorio', 'fecha', 'hora_inicio', 'hora_fin', 'estado', 'usuario')
    list_filter = ('estado', 'laboratorio', 'fecha')
    search_fields = ('laboratorio', 'usuario__username', 'motivo')
    ordering = ('-fecha', 'hora_inicio')
