# Generated by Django 3.0.5 on 2020-05-11 04:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('fintech_website', '0007_remove_amfidata_from_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='NIFTYdata',
            fields=[
                ('date', models.DateField(primary_key=True, serialize=False)),
                ('tri', models.DecimalField(decimal_places=2, max_digits=8)),
            ],
        ),
    ]
