from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_alter_articles_options_alter_articles_anons'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articles',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Data'),
        ),
    ]
