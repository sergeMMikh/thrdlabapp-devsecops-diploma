from django.shortcuts import render


# from django.http import HttpResponse


def index(request):
    content = {
        'title': 'Home',
        'side_bar_image': 'main/img/side_bar_home.png',
    }
    return render(request, 'main/index.html', content)


def about(request):
    content = {
        'title': 'About',
        'side_bar_image': 'main/img/side_bar_home.png',
    }
    return render(request, 'main/about.html', content)


def contacts(request):
    content = {
        'title': 'Contacts',
        'side_bar_image': 'main/img/side_for_furnace.png',
    }
    return render(request, 'main/contacts.html', content)
