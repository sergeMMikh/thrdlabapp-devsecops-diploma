from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import date, timedelta
from urllib.parse import urlencode
from itertools import groupby
from django.http import JsonResponse
from .models import Furnace, BookingOfFurnace, Equipment, BookingOfEquipment
from .forms import FurnaceBookingForm, EquipmentBookingForm


def home_view(request):
    template = 'main/furnaces.html'

    furnaces = Furnace.objects.select_related('laboratory').order_by(
        'laboratory__number',
        'name',
    )
    furnace_groups = []
    for location, location_furnaces in groupby(
        furnaces,
        key=lambda furnace: furnace.laboratory.number,
    ):
        grouped_furnaces = list(location_furnaces)
        furnace_groups.append(
            {
                'location': location,
                'laboratory_name': grouped_furnaces[0].laboratory.name,
                'furnaces': grouped_furnaces,
            },
        )

    context = {
        'title': 'Furnaces',
        'furnaces': furnaces,
        'furnace_groups': furnace_groups,
        'side_bar_image': 'main/img/side_bar_img.png',
    }

    return render(request, template, context)


def equipment_list_view(request):
    template = 'main/equipments.html'

    equipments = Equipment.objects.select_related('laboratory').order_by(
        'laboratory__number',
        'name',
    )

    context = {
        'title': 'Equipment',
        'equipments': equipments,
    }

    return render(request, template, context)


def equipment_booking_view(request):
    template = 'equipment_booking_form.html'

    if request.method == 'POST':
        form = EquipmentBookingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            action = request.POST.get('action', 'book')
            try:
                with transaction.atomic():
                    BookingOfEquipment.objects.create(
                        date=data['date'],
                        equipment=data['equipment'],
                        person=data['person'],
                        comments=data.get('comments') or None,
                    )
            except IntegrityError:
                form.add_error(None, 'This equipment is already booked for that date.')
            else:
                if action == 'book_and_next':
                    query = urlencode({
                        'person': data['person'].pk,
                        'equipment': data['equipment'].pk,
                        'date': (data['date'] + timedelta(days=1)).isoformat(),
                        'comments': data.get('comments') or '',
                    })
                    return redirect(f"{reverse('equipment_booking')}?{query}")
                equipment_query = urlencode({'equipment': data['equipment'].name})
                return redirect(f"{reverse('equipment')}?{equipment_query}")
    else:
        initial = {}
        person_id = request.GET.get('person')
        equipment_id = request.GET.get('equipment')
        if person_id:
            initial['person'] = person_id
        if equipment_id:
            initial['equipment'] = equipment_id
        if request.GET.get('date'):
            initial['date'] = request.GET['date']
        if 'comments' in request.GET:
            initial['comments'] = request.GET.get('comments', '')
        form = EquipmentBookingForm(initial=initial or None)

    context = {
        'title': 'Equipment booking',
        'form': form,
    }

    return render(request, template, context)


def furnace_booking_view(request):
    template = 'furnace_booking_form.html'

    if request.method == 'POST':
        form = FurnaceBookingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            action = request.POST.get('action', 'book')
            try:
                with transaction.atomic():
                    BookingOfFurnace.objects.create(
                        date=data['date'],
                        furnace=data['furnace'],
                        person=data['person'],
                        comments=data.get('comments') or None,
                    )
            except IntegrityError:
                form.add_error(None, 'This furnace is already booked for that date.')
            else:
                if action == 'book_and_next':
                    query = urlencode({
                        'person': data['person'].pk,
                        'furnace': data['furnace'].pk,
                        'date': (data['date'] + timedelta(days=1)).isoformat(),
                        'comments': data.get('comments') or '',
                    })
                    return redirect(f"{reverse('furnace_booking')}?{query}")
                furnace_query = urlencode({'furnace': data['furnace'].name})
                return redirect(f"{reverse('furnace')}?{furnace_query}")
    else:
        initial = {}
        person_id = request.GET.get('person')
        furnace_id = request.GET.get('furnace')
        if person_id:
            initial['person'] = person_id
        if furnace_id:
            initial['furnace'] = furnace_id
        if request.GET.get('date'):
            initial['date'] = request.GET['date']
        if 'comments' in request.GET:
            initial['comments'] = request.GET.get('comments', '')
        form = FurnaceBookingForm(initial=initial or None)

    context = {
        'title': 'Furnace booking',
        'form': form,
        'side_bar_image': 'main/img/side_bar_img.png',
    }

    return render(request, template, context)


def check_equipment_availability(request):
    """AJAX endpoint used by the booking form to tell whether a piece of
    equipment is already taken for the supplied date.  Accepts GET
    parameters ``equipment`` (pk) and ``date`` (ISO string).  Returns JSON
    ``{'available': bool}``.
    """
    equipment_id = request.GET.get('equipment')
    date_str = request.GET.get('date')
    available = True
    if equipment_id and date_str:
        try:
            # date input returns YYYY-MM-DD; let Python parse it directly
            booking_date = date.fromisoformat(date_str)
            exists = BookingOfEquipment.objects.filter(
                equipment_id=equipment_id,
                date=booking_date,
            ).exists()
            available = not exists
        except ValueError:
            # malformed date, just ignore
            available = True
    return JsonResponse({'available': available})


def check_furnace_availability(request):
    """Same as ``check_equipment_availability`` but for furnaces.``
    """
    furnace_id = request.GET.get('furnace')
    date_str = request.GET.get('date')
    available = True
    if furnace_id and date_str:
        try:
            booking_date = date.fromisoformat(date_str)
            exists = BookingOfFurnace.objects.filter(
                furnace_id=furnace_id,
                date=booking_date,
            ).exists()
            available = not exists
        except ValueError:
            available = True
    return JsonResponse({'available': available})


def furnace_book_list(request):
    template = 'furnace_booking_list.html'

    furnace_name = request.GET.get('furnace', 'Forno')
    furnace = Furnace.objects.filter(name=furnace_name).first()
    if furnace is None:
        return redirect(reverse('furnaces'))

    booking = BookingOfFurnace.objects.order_by('date').filter(
        furnace__name=furnace_name).reverse()

    book_list = []

    for book in booking:

        comments = str(book.comments)

        if comments == 'None':
            comments = ' '

        tmp_dict = {'id': book.id,
                    'date': book.date,
                    'user': book.person,
                    'comment': comments}

        book_list.append(tmp_dict)

    context = {'furnace': furnace,
               'date_today': date.today(),
               'booking_list': book_list,
               'side_bar_image': 'main/img/side_bar_img.png'}

    return render(request, template, context)


def equipment_book_list(request):
    template = 'equipment_booking_list.html'

    equipment_name = request.GET.get('equipment', 'Equipment')
    equipment = Equipment.objects.filter(name=equipment_name).first()
    if equipment is None:
        return redirect(reverse('equipments'))

    booking = BookingOfEquipment.objects.order_by('date').filter(
        equipment__name=equipment_name).reverse()

    book_list = []

    for book in booking:

        comments = str(book.comments)

        if comments == 'None':
            comments = ' '

        tmp_dict = {'id': book.id,
                    'date': book.date,
                    'user': book.person,
                    'comment': comments}

        book_list.append(tmp_dict)

    context = {'equipment': equipment,
               'date_today': date.today(),
               'booking_list': book_list}

    return render(request, template, context)


def delete_furnace_booking_view(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        furnace_name = request.POST.get('furnace_name')
        next_url = request.POST.get('next')
        if booking_id:
            booking = BookingOfFurnace.objects.filter(id=booking_id).first()
            if booking and booking.date >= date.today():
                booking.delete()
        if next_url:
            return redirect(next_url)
        if furnace_name:
            furnace_query = urlencode({'furnace': furnace_name})
            return redirect(f"{reverse('furnace')}?{furnace_query}")
    return redirect(reverse('furnaces'))


def delete_equipment_booking_view(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        equipment_name = request.POST.get('equipment_name')
        next_url = request.POST.get('next')
        if booking_id:
            booking = BookingOfEquipment.objects.filter(id=booking_id).first()
            if booking and booking.date >= date.today():
                booking.delete()
        if next_url:
            return redirect(next_url)
        if equipment_name:
            return redirect(
                f"{reverse('equipment')}?{urlencode({'equipment': equipment_name})}",
            )
    return redirect(reverse('equipments'))
