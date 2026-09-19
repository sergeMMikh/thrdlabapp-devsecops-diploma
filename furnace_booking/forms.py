from django import forms
from django.utils import timezone

from .models import Furnace, Equipment
from users.models import Person


class BookingActionForm(forms.Form):
    action = forms.ChoiceField(
        choices=(('book', 'Book'), ('book_and_next', 'Book and next')),
        required=False,
        widget=forms.HiddenInput,
    )


class FurnaceBookingForm(BookingActionForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.all().order_by('first_name', 'surname'),
        label='Person',
    )
    furnace = forms.ModelChoiceField(
        queryset=Furnace.objects.select_related('laboratory').order_by(
            'laboratory__number',
            'name',
        ),
        label='Furnace',
    )
    date = forms.DateField(
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Date',
    )
    comments = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Comments',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['min'] = timezone.localdate().isoformat()

    def clean_date(self):
        booking_date = self.cleaned_data['date']
        if booking_date < timezone.localdate():
            raise forms.ValidationError('You cannot book for a past date.')
        return booking_date


class EquipmentBookingForm(BookingActionForm):
    person = forms.ModelChoiceField(
        queryset=Person.objects.all().order_by('first_name', 'surname'),
        label='Person',
    )
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.select_related('laboratory').order_by(
            'laboratory__number',
            'name',
        ),
        label='Equipment',
    )
    date = forms.DateField(
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Date',
    )
    comments = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Comments',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['min'] = timezone.localdate().isoformat()

    def clean_date(self):
        booking_date = self.cleaned_data['date']
        if booking_date < timezone.localdate():
            raise forms.ValidationError('You cannot book for a past date.')
        return booking_date
