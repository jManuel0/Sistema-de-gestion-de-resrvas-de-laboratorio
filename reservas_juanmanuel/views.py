from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView


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


class HomeView(LoginRequiredMixin, RolBasicoMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['es_admin'] = es_admin(self.request.user)
        ctx['es_docente'] = es_docente(self.request.user)
        return ctx
