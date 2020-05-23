# Generated by Django 3.0.5 on 2020-05-23 05:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('fintech_website', '0014_delete_niftydata'),
    ]

    operations = [
        migrations.CreateModel(
            name='NIFTYdata',
            fields=[
                ('date', models.DateField(primary_key=True, serialize=False)),
                ('TRI', models.DecimalField(decimal_places=2, max_digits=8)),
            ],
        ),
    ]
