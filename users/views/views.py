from django.shortcuts import render
from django.utils import timezone

from furnace_booking.models import BookingOfEquipment, BookingOfFurnace
from ..models import Person


def home_view(request):
    template = '../templates/base.html'
    context = {}

    return render(request, template, context)


def people_list_view(request):
    template = 'users/people.html'
    people = list(Person.objects.all().order_by('first_name', 'surname'))
    people_rows = [people[i:i + 2] for i in range(0, len(people), 2)]

    context = {
        'title': 'People',
        'people_rows': people_rows,
        'side_bar_image': 'main/img/side_bar_person.png',
    }

    return render(request, template, context)


def person_detail_view(request, person_id):
    template = 'users/person_detail.html'
    person = Person.objects.get(id=person_id)
    today = timezone.localdate()

    furnace_bookings = BookingOfFurnace.objects.select_related(
        'furnace',
    ).filter(
        person=person,
        date__gte=today,
    )
    equipment_bookings = BookingOfEquipment.objects.select_related(
        'equipment',
    ).filter(
        person=person,
        date__gte=today,
    )

    bookings = [
        {
            'id': booking.id,
            'date': booking.date,
            'kind': 'Furnace',
            'kind_key': 'furnace',
            'name': booking.furnace.name,
            'comments': booking.comments or '',
        }
        for booking in furnace_bookings
    ] + [
        {
            'id': booking.id,
            'date': booking.date,
            'kind': 'Equipment',
            'kind_key': 'equipment',
            'name': booking.equipment.name,
            'comments': booking.comments or '',
        }
        for booking in equipment_bookings
    ]
    bookings.sort(
        key=lambda booking: (booking['date'], booking['kind'], booking['name']),
        reverse=True,
    )
    today_bookings = [booking for booking in bookings if booking['date'] == today]

    context = {
        'title': 'Person',
        'person': person,
        'side_bar_image': 'main/img/side_bar_person.png',
        'date_today': today,
        'today_bookings': today_bookings,
        'bookings': bookings,
    }

    return render(request, template, context)


def today_equipment_bookings_view(request):
    template = 'users/today_equipment_bookings.html'
    today = timezone.localdate()

    equipment_bookings = BookingOfEquipment.objects.select_related(
        'equipment',
        'equipment__laboratory',
        'person',
    ).filter(
        date=today,
    ).order_by(
        'equipment__laboratory__number',
        'equipment__name',
        'person__first_name',
        'person__surname',
    )
    furnace_bookings = BookingOfFurnace.objects.select_related(
        'furnace',
        'furnace__laboratory',
        'person',
    ).filter(
        date=today,
    ).order_by(
        'furnace__laboratory__number',
        'furnace__name',
        'person__first_name',
        'person__surname',
    )

    bookings = [
        {
            'id': booking.id,
            'date': booking.date,
            'kind': 'Equipment',
            'item_name': booking.equipment.name,
            'item_location': booking.equipment.location,
            'person_id': booking.person.id,
            'person_name': str(booking.person),
            'person_email': booking.person.email or '',
            'person_phone': booking.person.telephone_number or '',
        }
        for booking in equipment_bookings
    ] + [
        {
            'id': booking.id,
            'date': booking.date,
            'kind': 'Furnace',
            'item_name': booking.furnace.name,
            'item_location': booking.furnace.location,
            'person_id': booking.person.id,
            'person_name': str(booking.person),
            'person_email': booking.person.email or '',
            'person_phone': booking.person.telephone_number or '',
        }
        for booking in furnace_bookings
    ]
    bookings.sort(
        key=lambda booking: (
            booking['item_location'],
            booking['kind'],
            booking['item_name'],
            booking['person_name'],
        ),
    )

    context = {
        'title': "Today's bookings",
        'date_today': today,
        'bookings': bookings,
        'side_bar_image': 'main/img/side_bar_person.png',
    }

    return render(request, template, context)
