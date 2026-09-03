from django.contrib import admin

from .models import Articles


@admin.register(Articles)
class ArticlesAdmin(admin.ModelAdmin):
    list_display = 'title', 'author', 'date', 'anons', 'full_text'
    search_fields = ('title', 'date')
