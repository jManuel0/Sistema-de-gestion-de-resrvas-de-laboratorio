import csv
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .forms import RegistroUsuarioForm, ReservaForm
from .models import Reserva


class BootstrapAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].label = 'Usuario o correo'
        self.fields['username'].widget.attrs.setdefault('class', 'form-control')
        self.fields['username'].widget.attrs.setdefault('placeholder', 'Usuario o correo')
        self.fields['password'].widget.attrs.setdefault('class', 'form-control')

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        if username_or_email and '@' in username_or_email:
            user = User.objects.filter(email__iexact=username_or_email).first()
            if user:
                self.cleaned_data['username'] = user.get_username()
        return super().clean()


class UsuarioLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = BootstrapAuthenticationForm


class UsuarioLogoutView(LogoutView):
    pass


class UsuarioRegistroView(CreateView):
    form_class = RegistroUsuarioForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('reservas:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('reservas:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        nombre_grupo = form.cleaned_data['rol']
        grupo, _ = Group.objects.get_or_create(name=nombre_grupo)
        self.object.groups.add(grupo)
        self.object.is_staff = nombre_grupo == 'Administrador'
        self.object.save()
        login(self.request, self.object)
        messages.success(self.request, 'Tu cuenta fue creada correctamente.')
        return response


def es_admin(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.is_staff or user.groups.filter(name='Administrador').exists())
    )


def es_docente(user) -> bool:
    return bool(user and user.is_authenticated and user.groups.filter(name='Docente').exists())


def es_estudiante(user) -> bool:
    return bool(user and user.is_authenticated and user.groups.filter(name='Estudiante').exists())


class RolBasicoMixin(UserPassesTestMixin):
    def test_func(self):
        return es_admin(self.request.user) or es_docente(self.request.user) or es_estudiante(self.request.user)


def reservas_permitidas_para(user):
    reservas = Reserva.objects.select_related('usuario')
    if es_admin(user):
        return reservas
    if es_docente(user):
        return reservas.filter(usuario=user)
    return reservas.filter(estado=Reserva.Estados.APROBADA)


def aplicar_filtros_reservas(reservas, request):
    laboratorio = (request.GET.get('laboratorio') or '').strip()
    fecha = (request.GET.get('fecha') or '').strip()

    if laboratorio:
        reservas = reservas.filter(laboratorio__icontains=laboratorio)
    if fecha:
        reservas = reservas.filter(fecha=fecha)

    return reservas


class HomeView(LoginRequiredMixin, RolBasicoMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['es_admin'] = es_admin(self.request.user)
        ctx['es_docente'] = es_docente(self.request.user)
        ctx['es_estudiante'] = es_estudiante(self.request.user)
        return ctx


class ReservaListView(LoginRequiredMixin, RolBasicoMixin, ListView):
    model = Reserva
    template_name = 'reservas_juanmanuel/lista_reservas.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        reservas = reservas_permitidas_para(self.request.user)
        return aplicar_filtros_reservas(reservas, self.request)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        reservas = ctx['reservas']
        ctx['es_admin'] = es_admin(self.request.user)
        ctx['es_docente'] = es_docente(self.request.user)
        ctx['es_estudiante'] = es_estudiante(self.request.user)
        ctx['filtro_laboratorio'] = (self.request.GET.get('laboratorio') or '').strip()
        ctx['filtro_fecha'] = (self.request.GET.get('fecha') or '').strip()
        ctx['total_reservas'] = reservas.count()
        ctx['reservas_pendientes'] = reservas.filter(estado=Reserva.Estados.PENDIENTE).count()
        ctx['reservas_aprobadas'] = reservas.filter(estado=Reserva.Estados.APROBADA).count()
        ctx['reservas_rechazadas'] = reservas.filter(estado=Reserva.Estados.RECHAZADA).count()
        return ctx


class DocenteRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return es_docente(self.request.user)


class ReservaCreateView(LoginRequiredMixin, DocenteRequiredMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas_juanmanuel/reserva_form.html'
    success_url = reverse_lazy('reservas:lista_reservas')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Reserva creada correctamente')
        return super().form_valid(form)


class ReservaPendientePropiaMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        reserva = self.get_object()
        return (
            es_docente(self.request.user)
            and reserva.usuario == self.request.user
            and reserva.estado == Reserva.Estados.PENDIENTE
        )


class ReservaUpdateView(ReservaPendientePropiaMixin, UpdateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas_juanmanuel/reserva_form.html'
    success_url = reverse_lazy('reservas:lista_reservas')

    def form_valid(self, form):
        messages.success(self.request, 'Reserva actualizada correctamente')
        return super().form_valid(form)


class ReservaDeleteView(ReservaPendientePropiaMixin, DeleteView):
    model = Reserva
    template_name = 'reservas_juanmanuel/reserva_confirm_delete.html'
    success_url = reverse_lazy('reservas:lista_reservas')

    def form_valid(self, form):
        messages.success(self.request, 'Reserva cancelada correctamente')
        return super().form_valid(form)


class ReservaCambiarEstadoView(LoginRequiredMixin, UserPassesTestMixin, View):
    nuevo_estado = None
    mensaje = ''

    def test_func(self):
        return es_admin(self.request.user)

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        if reserva.estado != Reserva.Estados.PENDIENTE:
            messages.error(request, 'Solo se pueden aprobar o rechazar reservas pendientes.')
            return redirect('reservas:lista_reservas')

        reserva.estado = self.nuevo_estado
        reserva.save()
        messages.success(request, self.mensaje)
        return redirect('reservas:lista_reservas')


class ReservaAprobarView(ReservaCambiarEstadoView):
    nuevo_estado = Reserva.Estados.APROBADA
    mensaje = 'Reserva aprobada correctamente'


class ReservaRechazarView(ReservaCambiarEstadoView):
    nuevo_estado = Reserva.Estados.RECHAZADA
    mensaje = 'Reserva rechazada correctamente'


class EstadisticasView(LoginRequiredMixin, RolBasicoMixin, TemplateView):
    template_name = 'reservas_juanmanuel/estadisticas.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        reservas = reservas_permitidas_para(self.request.user)
        ctx['total_reservas'] = reservas.count()
        ctx['reservas_por_estado'] = reservas.values('estado').annotate(total=Count('id')).order_by('estado')
        ctx['reservas_por_laboratorio'] = reservas.values('laboratorio').annotate(total=Count('id')).order_by('laboratorio')
        return ctx


class ReservaCSVExportView(LoginRequiredMixin, RolBasicoMixin, View):
    def get(self, request):
        reservas = reservas_permitidas_para(request.user)
        reservas = aplicar_filtros_reservas(reservas, request)

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="reservas.csv"'

        writer = csv.writer(response)
        writer.writerow(['Laboratorio', 'Fecha', 'Hora inicio', 'Hora fin', 'Estado', 'Usuario', 'Motivo'])
        for reserva in reservas:
            writer.writerow([
                reserva.laboratorio,
                reserva.fecha,
                reserva.hora_inicio,
                reserva.hora_fin,
                reserva.get_estado_display(),
                reserva.usuario.username,
                reserva.motivo,
            ])

        return response
