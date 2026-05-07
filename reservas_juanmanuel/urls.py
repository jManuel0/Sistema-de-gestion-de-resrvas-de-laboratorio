from django.urls import path

from . import views

app_name = 'reservas'

urlpatterns = [
    path('login/', views.UsuarioLoginView.as_view(), name='login'),
    path('registro/', views.UsuarioRegistroView.as_view(), name='registro'),
    path('logout/', views.UsuarioLogoutView.as_view(), name='logout'),
    path('', views.HomeView.as_view(), name='home'),
]

