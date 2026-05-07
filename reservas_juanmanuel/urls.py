from django.urls import path

from . import views

app_name = 'reservas'

urlpatterns = [
    path('login/', views.UsuarioLoginView.as_view(), name='login'),
    path('logout/', views.UsuarioLogoutView.as_view(), name='logout'),
    path('', views.ReservaListView.as_view(), name='lista'),
    path('reservas/nueva/', views.ReservaCreateView.as_view(), name='crear'),
    path('reservas/<int:pk>/editar/', views.ReservaUpdateView.as_view(), name='editar'),
    path('reservas/<int:pk>/eliminar/', views.ReservaDeleteView.as_view(), name='eliminar'),
    path('reservas/<int:pk>/estado/', views.ReservaEstadoUpdateView.as_view(), name='cambiar_estado'),
    path('reportes/reservas.csv', views.ReservaCSVExportView.as_view(), name='csv'),
    path('estadisticas/', views.EstadisticasView.as_view(), name='estadisticas'),
]

