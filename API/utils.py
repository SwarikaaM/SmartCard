from django.urls import reverse
from rest_framework.response import Response
from .models import Device
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets, pyotp, uuid
from django.core.mail import send_mail
from django.conf import settings
from .models import manage_validate_request
from django.template.loader import render_to_string


class is_authenticatedResponse(Response):
    def __init__(self, **kwargs):
        datas = {**kwargs}
        super().__init__(datas)


@receiver(post_save, sender=Device)
def create_api_key(sender, instance, created, **kwargs):
    if created and not instance.API_Key:
        instance.API_Key = secrets.token_hex(32)
        instance.save(update_fields=['API_Key'])


def send_validator_email(user, requests):
    def otp(length=10, expiry=180):
        secret_key = pyotp.random_base32()
        totp = pyotp.totp.TOTP(secret_key, interval=expiry, digits=length)
        uid = uuid.uuid4()
        return totp, uid

    if not user.Email:
        return False

    OTP_, uid = otp()
    confirm_url = requests.build_absolute_uri(reverse('Everification', args=[uid.hex, OTP_.now()]))

    data = {
        'name': user.First_Name + ' ' + user.Last_Name if user.Last_Name else user.First_Name,
        'link': confirm_url,
    }

    subject = "Are You Accessing Your Data?"
    body = render_to_string('API/email_veri.html', data)
    from_email = settings.EMAIL_HOST_USER
    to_email = [user.Email]
    rst = send_mail(subject, '', from_email, to_email, html_message=body, fail_silently=False)
    if rst:
        manage_validate_request.objects.create(User=user, OTP=OTP_.secret, UUID=uid, Is_Validated=False)
        req = manage_validate_request.objects.filter(UUID=uid, User=user).first()
        return req
    return False, None, None


def verify_validator_email(uid, otp):
    if not uid or not otp:
        return False
    req = manage_validate_request.objects.filter(UUID=uuid.UUID(uid)).first()
    if not req:
        return False, 'This Link Is Invalid Or Expired Or Already Used'
    if req.Is_Validated:
        return False, 'This Link Is Already Used'
    secret = req.OTP
    totp = pyotp.totp.TOTP(secret, interval=180, digits=10)
    if totp.verify(str(otp)):
        req.Is_Validated = True
        req.save()
        return True, 'Access Granted'
    return False, 'Invalid Verification Code'
