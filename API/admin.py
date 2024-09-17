from django.contrib import admin
from .models import Device


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('Device_Name', 'Is_Active')
    search_fields = ('Device_Name', 'API_Key')
    list_filter = ('Is_Active',)
    readonly_fields = ('API_Key',)


admin.site.register(Device, DeviceAdmin)
