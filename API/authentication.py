from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import Device


class DeviceAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            raise exceptions.AuthenticationFailed("API KEY NOT PROVIDED")
        try:
            device = Device.objects.get(API_Key=api_key)
            if not device.Is_Active:
                raise exceptions.NotAuthenticated("API KEY IS NOT ACTIVE")
            return (device, None)
        except Device.DoesNotExist:
            raise exceptions.NotAuthenticated("INVALID API KEY")
