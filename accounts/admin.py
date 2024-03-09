from django.contrib import admin
from .models import CustomUser
# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('userloginname', 'password','email', 'is_active', 'date_joined')
    search_fields = ('userloginname', 'email')


