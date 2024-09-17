from django.db import models
import secrets


# Register your models here.
class Device(models.Model):
    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"

    Device_Name = models.CharField(max_length=100)
    API_Key = models.CharField(max_length=64, unique=True, blank=True, null=True)
    Is_Active = models.BooleanField(default=True)

    def __str__(self):
        return self.Device_Name


class manage_validate_request(models.Model):
    class Meta:
        verbose_name = "Validate Request"
        verbose_name_plural = "Validate Requests"

    User = models.ForeignKey('Core.User', on_delete=models.CASCADE)
    OTP = models.CharField(max_length=32, blank=True)
    UUID = models.UUIDField(max_length=32, blank=True)
    Created_At = models.DateTimeField(auto_now_add=True)
    Is_Validated = models.BooleanField(default=False)

    def __str__(self):
        return self.User
