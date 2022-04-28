from django.contrib import admin
from .models import User, TimeClock, TimeSheet

# Register your models here.
admin.site.register(User)
admin.site.register(TimeSheet)
admin.site.register(TimeClock)