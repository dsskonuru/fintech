# Generated by Django 3.0.5 on 2020-05-12 04:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('fintech_website', '0009_auto_20200511_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amfidata',
            name='code',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='amfidata',
            name='name',
            field=models.TextField(primary_key=True, serialize=False),
        ),
    ]
