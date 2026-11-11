from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    path('', views.panel_recepcion, name='panel_recepcion'),
    path('agendar/<int:bloque_id>/', views.agendar_cita, name='agendar_cita'),
    path('cita/<int:cita_id>/', views.detalle_cita, name='detalle_cita'),
    path('cita/<int:cita_id>/estado/', views.cambiar_estado_cita, name='cambiar_estado_cita'),
    path('api/paciente/buscar/', views.buscar_paciente_api, name='buscar_paciente_api'),
]

