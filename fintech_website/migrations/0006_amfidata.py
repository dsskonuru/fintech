# Generated by Django 3.0.5 on 2020-05-10 17:02

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('fintech_website', '0005_delete_amfidatabase'),
    ]

    operations = [
        migrations.CreateModel(
            name='AMFIdata',
            fields=[
                ('code', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('from_date', models.DateField()),
            ],
        ),
    ]