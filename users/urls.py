from django.urls import path

from .views import views


urlpatterns = [
    path('people/', views.people_list_view, name='people'),
    path(
        'people/today-equipment-bookings/',
        views.today_equipment_bookings_view,
        name='today_equipment_bookings',
    ),
    path('people/<int:person_id>/', views.person_detail_view, name='person_detail'),
]
