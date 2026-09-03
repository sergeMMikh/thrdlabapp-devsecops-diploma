from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='furnaces'),
    path(
        'furnace-booking/',
        views.furnace_booking_view,
        name='furnace_booking',
    ),
    path(
        'api/furnace-available/',
        views.check_furnace_availability,
        name='check_furnace_availability',
    ),
    path(
        'furnace-booking/delete/',
        views.delete_furnace_booking_view,
        name='delete_furnace_booking',
    ),
    path('equipments/', views.equipment_list_view, name='equipments'),
    path(
        'equipment-booking/',
        views.equipment_booking_view,
        name='equipment_booking',
    ),
    path(
        'equipment-booking/delete/',
        views.delete_equipment_booking_view,
        name='delete_equipment_booking',
    ),
    # AJAX helpers
    path(
        'api/equipment-available/',
        views.check_equipment_availability,
        name='check_equipment_availability',
    ),
    path('furnace', views.furnace_book_list, name='furnace'),
    path('equipment', views.equipment_book_list, name='equipment'),
]
