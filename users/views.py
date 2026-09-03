from django.shortcuts import render

from .models import Person


def people_list_view(request):
    template = 'users/people.html'
    people = Person.objects.all().order_by('first_name', 'surname')

    context = {
        'title': 'People',
        'people': people,
    }

    return render(request, template, context)
