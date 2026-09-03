from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import (
    Equipment,
    Furnace,
    BookingOfEquipment,
    BookingOfFurnace,
    Laboratory,
)
from users.models import Person


class AvailabilityAPITest(TestCase):
    def setUp(self):
        # minimal objects required for bookings
        # Person has only name fields
        self.person = Person.objects.create(first_name='Test', surname='User')
        self.laboratory = Laboratory.objects.create(
            number='Lab',
            name='Test Laboratory',
        )
        self.equipment = Equipment.objects.create(
            name='Eq1',
            laboratory=self.laboratory,
        )
        self.furnace = Furnace.objects.create(
            name='F1',
            laboratory=self.laboratory,
            serviceable=True,
            max_temperature=100,
            min_temperature=0,
            is_clean=True,
        )
        self.today = date.today()

    def test_equipment_available_when_no_booking(self):
        url = reverse('check_equipment_availability')
        resp = self.client.get(url, {
            'equipment': self.equipment.pk,
            'date': self.today.isoformat(),
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {'available': True})

    def test_equipment_not_available_when_booked(self):
        BookingOfEquipment.objects.create(
            date=self.today,
            equipment=self.equipment,
            person=self.person,
        )
        url = reverse('check_equipment_availability')
        resp = self.client.get(url, {
            'equipment': self.equipment.pk,
            'date': self.today.isoformat(),
        })
        self.assertEqual(resp.json(), {'available': False})

    def test_furnace_available_when_no_booking(self):
        url = reverse('check_furnace_availability')
        resp = self.client.get(url, {
            'furnace': self.furnace.pk,
            'date': self.today.isoformat(),
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {'available': True})

    def test_furnace_not_available_when_booked(self):
        BookingOfFurnace.objects.create(
            date=self.today,
            furnace=self.furnace,
            person=self.person,
        )
        url = reverse('check_furnace_availability')
        resp = self.client.get(url, {
            'furnace': self.furnace.pk,
            'date': self.today.isoformat(),
        })
        self.assertEqual(resp.json(), {'available': False})
