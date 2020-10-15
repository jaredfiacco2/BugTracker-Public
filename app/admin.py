from django.contrib import admin

# Register your models here.
from .models import ContactInfo, Usecases
admin.site.register(ContactInfo)
admin.site.register(Usecases)

