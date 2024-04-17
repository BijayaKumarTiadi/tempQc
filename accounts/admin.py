from django.contrib import admin
from .models import CustomUser,AppModule,OTP
from accounts.models import ChangeLog
# Register your models here.


#For Django Admin Page view

admin.site.site_header = "Renuka Softech Admin"
admin.site.site_title = "SmartMIS Admin Panel"
admin.site.index_title = "Welcome to SmartMIS Admin"


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('userloginname', 'password','email', 'is_active', 'date_joined')
    search_fields = ('userloginname', 'email')



class AppModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description', 'url')

admin.site.register(AppModule, AppModuleAdmin)


class OTPAdmin(admin.ModelAdmin):
    list_display = ('email',)
    # list_filter = ('is_active',)
    # search_fields = ('name', 'description', 'url')

admin.site.register(OTP, OTPAdmin)




#for the log entry 
@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'object_id','object_repr', 'get_action_flag_display', 'user')
    list_filter = ('action_flag',)
    search_fields = ('object_repr', 'change_message', 'user__username')
    #remove below comment to make it readonly
    # readonly_fields = ('action_time', 'object_id', 'object_repr', 'action_flag', 'change_message', 'content_type', 'user')
    date_hierarchy = 'action_time'
    ordering = ('-action_time',)
