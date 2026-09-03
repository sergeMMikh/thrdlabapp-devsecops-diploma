from django.db import models
from django.utils import timezone
from users.models import Person


class Articles(models.Model):
    title = models.CharField(verbose_name='Title', max_length=100, default='News')
    date = models.DateField(verbose_name='Data', default=timezone.now)
    author = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Author',
        related_name='notes',
    )
    anons = models.CharField(verbose_name='Anons', max_length=100, default='Anons')
    full_text = models.TextField(verbose_name='Article contetn')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/news/{self.id}'

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'
