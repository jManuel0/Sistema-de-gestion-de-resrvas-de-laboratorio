<<<<<<< HEAD
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .forms import RegistroUsuarioForm
=======
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .forms import RegistroUsuarioForm, ReservaForm
from .models import Reserva
>>>>>>> 8684703b2debc175363953c4ed2670749b7bd7a4


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


class UsuarioRegistroView(CreateView):
    form_class = RegistroUsuarioForm
    template_name = 'registration/register.html'
<<<<<<< HEAD
=======
    success_url = reverse_lazy('reservas:home')
>>>>>>> 8684703b2debc175363953c4ed2670749b7bd7a4

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('reservas:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
<<<<<<< HEAD
        grupo_docente, _ = Group.objects.get_or_create(name='Docente')
        self.object.groups.add(grupo_docente)
        login(self.request, self.object)
        messages.success(self.request, 'Tu cuenta fue creada y quedaste registrado como docente.')
        return response

    def get_success_url(self):
        return redirect('reservas:home').url

=======
        nombre_grupo = form.cleaned_data['rol']
        grupo, _ = Group.objects.get_or_create(name=nombre_grupo)
        self.object.groups.add(grupo)
        if nombre_grupo == 'Administrador':
            self.object.is_staff = True
            self.object.save()
        login(self.request, self.object)
        messages.success(self.request, 'Tu cuenta fue creada correctamente.')
        return response

>>>>>>> 8684703b2debc175363953c4ed2670749b7bd7a4

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


class HomeView(LoginRequiredMixin, RolBasicoMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['es_admin'] = es_admin(self.request.user)
        ctx['es_docente'] = es_docente(self.request.user)
        return ctx


class ReservaListView(LoginRequiredMixin, RolBasicoMixin, ListView):
    model = Reserva
    template_name = 'reservas_juanmanuel/lista_reservas.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        reservas = Reserva.objects.select_related('usuario')
        if es_admin(self.request.user):
            return reservas
        return reservas.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['es_admin'] = es_admin(self.request.user)
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
