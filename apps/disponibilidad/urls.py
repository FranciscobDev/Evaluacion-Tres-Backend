from django.urls import path
from . import views

app_name = 'disponibilidad'

urlpatterns = [
    path('mi-agenda/', views.mi_agenda, name='mi_agenda'),
    path('publicar/', views.publicar_bloque, name='publicar_bloque'),
    path('bloque/<int:id>/eliminar/', views.eliminar_bloque, name='eliminar_bloque'),
    path('cita/<int:id>/nota/', views.actualizar_nota_clinica, name='actualizar_nota_clinica'),
]

