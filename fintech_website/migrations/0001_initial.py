# Generated by Django 3.0.5 on 2020-05-10 06:34

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AMFIDatabase',
            fields=[
                ('code', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('from_date', models.DateField()),
            ],
        ),
    ]
