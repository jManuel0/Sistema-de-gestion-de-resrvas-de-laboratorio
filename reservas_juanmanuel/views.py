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

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('reservas:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        grupo_docente, _ = Group.objects.get_or_create(name='Docente')
        self.object.groups.add(grupo_docente)
        login(self.request, self.object)
        messages.success(self.request, 'Tu cuenta fue creada y quedaste registrado como docente.')
        return response

    def get_success_url(self):
        return redirect('reservas:home').url


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
