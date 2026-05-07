from django.urls import path

from . import views

app_name = 'reservas'

urlpatterns = [
    path('login/', views.UsuarioLoginView.as_view(), name='login'),
    path('registro/', views.UsuarioRegistroView.as_view(), name='registro'),
    path('logout/', views.UsuarioLogoutView.as_view(), name='logout'),
    path('reservas/', views.ReservaListView.as_view(), name='lista_reservas'),
    path('reservas/crear/', views.ReservaCreateView.as_view(), name='crear_reserva'),
    path('reservas/<int:pk>/editar/', views.ReservaUpdateView.as_view(), name='editar_reserva'),
    path('reservas/<int:pk>/eliminar/', views.ReservaDeleteView.as_view(), name='eliminar_reserva'),
    path('reservas/<int:pk>/aprobar/', views.ReservaAprobarView.as_view(), name='aprobar_reserva'),
    path('reservas/<int:pk>/rechazar/', views.ReservaRechazarView.as_view(), name='rechazar_reserva'),
    path('', views.HomeView.as_view(), name='home'),
]

