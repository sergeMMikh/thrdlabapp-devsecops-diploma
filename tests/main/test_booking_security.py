from datetime import date

import pytest
from django.urls import reverse

from furnace_booking.models import (
    BookingOfEquipment,
    BookingOfFurnace,
    Equipment,
    Furnace,
    Laboratory,
)
from users.models import Person


pytestmark = pytest.mark.django_db


@pytest.fixture(params=['furnace', 'equipment'])
def booking_case(request):
    kind = request.param
    laboratory = Laboratory.objects.create(number='Security', name='Security lab')
    person = Person.objects.create(first_name='Test', surname='Person')
    if kind == 'furnace':
        resource = Furnace.objects.create(
            name='Test furnace', laboratory=laboratory, serviceable=True,
            max_temperature=1000, min_temperature=20, is_clean=True,
        )
        booking_model = BookingOfFurnace
    else:
        resource = Equipment.objects.create(name='Test equipment', laboratory=laboratory)
        booking_model = BookingOfEquipment
    return kind, resource, person, booking_model


@pytest.mark.parametrize('next_url', [
    'https://attacker.example/',
    '//attacker.example/',
    r'/\attacker.example/',
    'javascript:alert(1)',
    'https://testserver.attacker.example/',
    'http://testserver/',  # HTTPS requests must not redirect to HTTP.
])
def test_delete_rejects_unsafe_redirect(client, booking_case, next_url):
    kind, resource, person, model = booking_case
    booking = model.objects.create(
        **{kind: resource}, person=person, date=date.today(),
    )
    response = client.post(reverse(f'delete_{kind}_booking'), {
        'booking_id': booking.pk,
        'next': next_url,
    }, secure=True)
    fallback = 'furnaces' if kind == 'furnace' else 'equipments'
    assert response.status_code == 302
    assert response.url == reverse(fallback)
    assert not model.objects.filter(pk=booking.pk).exists()


@pytest.mark.parametrize('next_url', ['/furnaces/', 'https://testserver/furnaces/'])
def test_delete_preserves_safe_redirect(client, booking_case, next_url):
    kind, _, _, _ = booking_case
    response = client.post(reverse(f'delete_{kind}_booking'), {
        'next': next_url,
    }, secure=True)
    assert response.url == next_url


@pytest.mark.parametrize('action', ['invalid', 'book', 'book_and_next', ''])
def test_booking_validates_action(client, booking_case, action):
    kind, resource, person, model = booking_case
    response = client.post(reverse(f'{kind}_booking'), {
        kind: resource.pk,
        'person': person.pk,
        'date': date.today().isoformat(),
        'action': action,
    })
    if action == 'invalid':
        assert response.status_code == 200
        assert 'action' in response.context['form'].errors
        assert not model.objects.exists()
    else:
        assert response.status_code == 302
        assert model.objects.count() == 1
        if action == 'book_and_next':
            assert response.url.startswith(reverse(f'{kind}_booking') + '?')
