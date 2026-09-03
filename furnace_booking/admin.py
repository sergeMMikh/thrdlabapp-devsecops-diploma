from django.contrib import admin

from furnace_booking.models import (
    Furnace,
    BookingOfFurnace,
    Equipment,
    BookingOfEquipment,
    Laboratory,
)


class BookingOfFurnaceInLine(admin.TabularInline):
    model = BookingOfFurnace
    extra = 3


class BookingOfEquipmentInLine(admin.TabularInline):
    model = BookingOfEquipment
    extra = 3


@admin.register(Laboratory)
class LaboratoryAdmin(admin.ModelAdmin):
    list_display = ('number', 'name')
    search_fields = ('number', 'name')


@admin.register(Furnace)
class FurnaceAdmin(admin.ModelAdmin):
    list_display = 'name', 'laboratory', 'max_temperature', \
                   'min_temperature', 'is_clean', 'serviceable'
    fields = ['laboratory',
              'name',
              'max_temperature',
              'min_temperature',
              'is_clean',
              'serviceable']
    inlines = [BookingOfFurnaceInLine]
    list_filter = ('laboratory',)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'laboratory')
    fields = ('laboratory', 'name')
    inlines = [BookingOfEquipmentInLine]
    list_filter = ('laboratory',)


@admin.register(BookingOfFurnace)
class BookingOfFurnaceAdmin(admin.ModelAdmin):
    list_display = 'date', 'furnace', 'person', 'comments'
    list_filter = ('furnace',)


@admin.register(BookingOfEquipment)
class BookingOfEquipmentAdmin(admin.ModelAdmin):
    list_display = 'date', 'equipment', 'person', 'comments'
    list_filter = ('equipment',)
