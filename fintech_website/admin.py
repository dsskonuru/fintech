from django.contrib import admin

# Register your models here.
from .models import AMFIdata, NIFTYdata

admin.site.register(AMFIdata)
admin.site.register(NIFTYdata)
