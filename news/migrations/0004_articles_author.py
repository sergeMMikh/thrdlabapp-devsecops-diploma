from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_remove_person_name_remove_person_telefone_and_more'),
        ('news', '0003_alter_articles_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='articles',
            name='author',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='notes',
                to='users.person',
                verbose_name='Author',
            ),
        ),
    ]
