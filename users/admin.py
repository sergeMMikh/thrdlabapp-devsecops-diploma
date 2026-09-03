from django.contrib import admin

from users.models import User, Person


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'email_is_verified']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'surname', 'email', 'telephone_number']
