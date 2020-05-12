from django.db import models
from django.urls import reverse


class AMFIdata(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('model-detail-view', args=[str(self.id)])

    def get_code(self):
        return self.code


class NIFTYdata(models.Model):
    date = models.DateField(primary_key=True)
    TRI = models.DecimalField(decimal_places=2, max_digits=8)

    def __str__(self):
        return str(self.date) + str(self.TRI)

    def get_tri(self):
        return self.TRI

    def get_date(self):
        return self.date
