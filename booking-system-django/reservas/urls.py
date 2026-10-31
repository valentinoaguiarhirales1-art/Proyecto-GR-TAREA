from django.urls import path

from . import views

urlpatterns = [
    path('', views.resource_list, name='recursos'),
    path('recurso/<int:pk>/', views.resource_detail, name='recurso'),
    path('recurso/<int:pk>/slots/', views.slots_api, name='slots'),
    path('recurso/<int:pk>/mes/', views.month_api, name='mes'),
    path('recurso/<int:pk>/reservar/', views.book, name='reservar'),
    path('mis-reservas/', views.my_bookings, name='mis_reservas'),
    path('cancelar/<int:pk>/', views.cancel, name='cancelar'),
    path('panel/', views.dashboard, name='panel'),
    path('registro/', views.register, name='registro'),
]
