from django.contrib import admin

# Register your models here.
from .models import EstItemtypemaster, EstItemtypedetail

class EstItemtypemasterAdmin(admin.ModelAdmin):
    list_display = ('internalCartonType', 'CartonType',)  # Display these fields in the list view
    search_fields = ('internalCartonType', 'CartonType', )  # Add these fields to the search functionality
    list_filter = ('internalCartonType',)  # Add filter options for this field

admin.site.register(EstItemtypemaster, EstItemtypemasterAdmin)


class EstItemtypedetailAdmin(admin.ModelAdmin):
    list_display = ( 'label_name','default_value','isactive','isrequired','tooltip')  # Display these fields in the list view
    search_fields = ('label_name','int_id','master',)  # Add these fields to the search functionality
    list_filter = ('isactive','isrequired','master',)  # Add filter options for this field

admin.site.register(EstItemtypedetail, EstItemtypedetailAdmin)