from django.contrib import admin

# Register your models here.
from .models import NIFTYdata, AMFIdata

admin.site.register(AMFIdata)
admin.site.register(NIFTYdata)
