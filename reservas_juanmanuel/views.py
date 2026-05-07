import csv
from datetime import date

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .forms import ReservaEstadoForm, ReservaForm
from .models import Reserva


class BootstrapAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs.setdefault('class', 'form-control')
        self.fields['password'].widget.attrs.setdefault('class', 'form-control')


class UsuarioLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = BootstrapAuthenticationForm


class UsuarioLogoutView(LogoutView):
    pass


def es_admin(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.is_staff or user.groups.filter(name='Administrador').exists())
    )


def es_docente(user) -> bool:
    return bool(user and user.is_authenticated and user.groups.filter(name='Docente').exists())


class RolBasicoMixin(UserPassesTestMixin):
    def test_func(self):
        return es_admin(self.request.user) or es_docente(self.request.user)


class ReservaQuerysetMixin:
    def base_queryset(self):
        qs = Reserva.objects.select_related('usuario')
        if es_admin(self.request.user):
            return qs
        return qs.filter(usuario=self.request.user)


class ReservaListView(LoginRequiredMixin, RolBasicoMixin, ReservaQuerysetMixin, ListView):
    model = Reserva
    template_name = 'reservas/reserva_list.html'
    context_object_name = 'reservas'
    paginate_by = 20

    def get_queryset(self):
        qs = self.base_queryset()
        laboratorio = (self.request.GET.get('laboratorio') or '').strip()
        fecha = (self.request.GET.get('fecha') or '').strip()

        if laboratorio:
            qs = qs.filter(laboratorio__icontains=laboratorio)
        if fecha:
            qs = qs.filter(fecha=fecha)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filtro_laboratorio'] = (self.request.GET.get('laboratorio') or '').strip()
        ctx['filtro_fecha'] = (self.request.GET.get('fecha') or '').strip()
        ctx['es_admin'] = es_admin(self.request.user)
        return ctx


class ReservaCreateView(LoginRequiredMixin, RolBasicoMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas/reserva_form.html'
    success_url = reverse_lazy('reservas:lista')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.estado = Reserva.Estados.PENDIENTE
        return super().form_valid(form)


class SoloPendientePropietarioMixin(UserPassesTestMixin):
    def test_func(self):
        reserva: Reserva = self.get_object()
        return (
            reserva.usuario_id == self.request.user.id
            and reserva.estado == Reserva.Estados.PENDIENTE
        )


class ReservaUpdateView(LoginRequiredMixin, RolBasicoMixin, SoloPendientePropietarioMixin, UpdateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas/reserva_form.html'
    success_url = reverse_lazy('reservas:lista')


class ReservaDeleteView(LoginRequiredMixin, RolBasicoMixin, SoloPendientePropietarioMixin, DeleteView):
    model = Reserva
    template_name = 'reservas/reserva_confirm_delete.html'
    success_url = reverse_lazy('reservas:lista')


class AdminEstadoMixin(UserPassesTestMixin):
    def test_func(self):
        return es_admin(self.request.user)


class ReservaEstadoUpdateView(LoginRequiredMixin, AdminEstadoMixin, UpdateView):
    model = Reserva
    form_class = ReservaEstadoForm
    template_name = 'reservas/reserva_estado_form.html'
    success_url = reverse_lazy('reservas:lista')


class ReservaCSVExportView(LoginRequiredMixin, RolBasicoMixin, ReservaQuerysetMixin, View):
    def get(self, request, *args, **kwargs):
        qs = self.base_queryset()
        laboratorio = (request.GET.get('laboratorio') or '').strip()
        fecha = (request.GET.get('fecha') or '').strip()
        if laboratorio:
            qs = qs.filter(laboratorio__icontains=laboratorio)
        if fecha:
            qs = qs.filter(fecha=fecha)

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        nombre = f"reservas_{now().date().isoformat()}.csv"
        response['Content-Disposition'] = f'attachment; filename="{nombre}"'

        writer = csv.writer(response)
        writer.writerow(
            [
                'usuario',
                'laboratorio',
                'fecha',
                'hora_inicio',
                'hora_fin',
                'estado',
                'motivo',
                'fecha_creacion',
            ]
        )
        for r in qs:
            writer.writerow(
                [
                    r.usuario.get_username(),
                    r.laboratorio,
                    r.fecha.isoformat(),
                    r.hora_inicio.strftime('%H:%M'),
                    r.hora_fin.strftime('%H:%M'),
                    r.get_estado_display(),
                    r.motivo,
                    r.fecha_creacion.isoformat(sep=' ', timespec='seconds'),
                ]
            )
        return response


class EstadisticasView(LoginRequiredMixin, RolBasicoMixin, ReservaQuerysetMixin, TemplateView):
    template_name = 'reservas/estadisticas.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.base_queryset()

        hoy = date.today()
        ctx['total'] = qs.count()
        ctx['por_estado'] = list(qs.values('estado').annotate(total=Count('id')).order_by('estado'))
        ctx['por_laboratorio'] = list(
            qs.values('laboratorio').annotate(total=Count('id')).order_by('-total', 'laboratorio')
        )
        ctx['hoy'] = hoy
        ctx['es_admin'] = es_admin(self.request.user)
        return ctx
