from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.inicio, name='inicio'),

    # Catálogo y Operaciones CRUD de Tratamientos Odontológicos
    path('servicios/', views.servicios, name='servicios'),
    path('servicios/nuevo/', views.crear_tratamiento, name='crear_tratamiento'),
    path('servicios/<slug:slug>/', views.detalle_tratamiento, name='detalle_tratamiento'),
    path('servicios/<slug:slug>/editar/', views.editar_tratamiento, name='editar_tratamiento'),
    path('servicios/<slug:slug>/eliminar/', views.eliminar_tratamiento, name='eliminar_tratamiento'),

    # Cotizador / Presupuesto Transitorio en Sesión HTTP
    path('presupuesto/', views.ver_presupuesto, name='ver_presupuesto'),
    path('presupuesto/agregar/<int:tratamiento_id>/', views.agregar_al_presupuesto, name='agregar_al_presupuesto'),
    path('presupuesto/actualizar/<int:tratamiento_id>/', views.actualizar_item_presupuesto, name='actualizar_item_presupuesto'),
    path('presupuesto/eliminar/<int:tratamiento_id>/', views.eliminar_item_presupuesto, name='eliminar_item_presupuesto'),
    path('presupuesto/vaciar/', views.vaciar_presupuesto, name='vaciar_presupuesto'),
    path('presupuesto/confirmar/', views.confirmar_solicitud_presupuesto, name='confirmar_solicitud_presupuesto'),

    path('contacto/', views.contacto, name='contacto'),
]

