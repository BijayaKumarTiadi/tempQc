from django.contrib import admin
from .models import CustomUser,AppModule
# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('userloginname', 'password','email', 'is_active', 'date_joined')
    search_fields = ('userloginname', 'email')



class AppModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description', 'url')

admin.site.register(AppModule, AppModuleAdmin)
