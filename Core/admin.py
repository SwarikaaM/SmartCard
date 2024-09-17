from django.contrib import admin

from .models import *


# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ("First_Name", "Last_Name", "Email", "Phone_Number")
    list_filter = ["is_active", "Document_Status"]
    readonly_fields = ("password", "Documents")
    search_fields = ["First_Name", "Last_Name", "Email", "Phone_Number"]
    ordering = ["First_Name", "Last_Name"]
    fieldsets = [
        ("User Information",
         {"fields": ["RFID","First_Name", "Last_Name", "Email", "Phone_Number", "password"]}),
        ("Permissions", {"fields": ["is_superuser", "is_staff", "is_active"]}),
        ("Documents", {"fields": ["Documents", "Document_Status", "Rejection_Reason"]})
    ]


class User_DocumentAdmin(admin.ModelAdmin):
    list_display = ("User", "Aadhar_Card", "Pan_Card")
    search_fields = ["User__First_Name", "User__Last_Name", "User__Email", "User__Phone_Number"]
    ordering = ["User__First_Name", "User__Last_Name"]
    readonly_fields = ["User", "Document_Passcode"]
    fieldsets = [
        ("User Information", {"fields": ["User", "Document_Passcode"]}),
        ("Documents", {"fields": ["Aadhar_Card", "Pan_Card"]})
    ]


admin.site.register(User_Document, User_DocumentAdmin)
admin.site.register(User, UserAdmin)
