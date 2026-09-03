from django.db import models

from users.models import Person


class Laboratory(models.Model):
    number = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f'{self.number} - {self.name}'


class BaseEquipment(models.Model):
    # equipment name in laboratory specifications
    name = models.CharField(max_length=100)

    laboratory = models.ForeignKey(
        Laboratory,
        on_delete=models.PROTECT,
        related_name='%(class)ss',
        verbose_name='laboratory',
    )

    # ip = models.CharField(max_length=20, null=True, blank=True)
    # port = models.CharField(max_length=6, null=True, blank=True)

    # the current equipment user
    user = models.ManyToManyField(Person,
                                  related_name='%(class)s_users',
                                  blank=True)

    class Meta:
        abstract = True

    @property
    def location(self):
        return self.laboratory.number

    @property
    def laboratory_name(self):
        return self.laboratory.name


class Furnace(BaseEquipment):
    # technical furnace conditions: is it working (Tru) or broken (False)
    serviceable = models.BooleanField(verbose_name='available to use')

    # the maximum operating temperature
    max_temperature = models.PositiveIntegerField(
        verbose_name='max. temperature')

    # the minimum operating temperature
    min_temperature = models.PositiveIntegerField(
        verbose_name='min. temperature')

    # is furnace using for clean materials:
    # free from acids, alkaline, transition or volatilizing elements
    is_clean = models.BooleanField(verbose_name='for clean materials')

    def __str__(self):
        return self.name


class Equipment(BaseEquipment):
    def __str__(self):
        return self.name


class BookingOfFurnace(models.Model):
    date = models.DateField()
    furnace = models.ForeignKey(
        Furnace,
        on_delete=models.CASCADE,
        related_name='furnace',
    )

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='furnace_bookings',
    )

    comments = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(name='unique_booking_d_f',
                                               fields=['date',
                                                       'furnace'])]


class BookingOfEquipment(models.Model):
    date = models.DateField()
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='equipment',
    )

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='equipment_bookings',
    )

    comments = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(name='unique_booking_d_e',
                                               fields=['date',
                                                       'equipment'])]
