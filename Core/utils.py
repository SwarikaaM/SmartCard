from django.core.mail import send_mail
from django.conf import settings
import pyotp
from django.template.loader import render_to_string

from .models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str


class Register_cnf:
    def send_cnf_otp(self, email):
        def otp(length=4, expiry=120):
            secret_key = pyotp.random_base32()
            totp = pyotp.totp.TOTP(secret_key, interval=expiry, digits=length)
            return totp

        if not email:
            return False

        OTP_ = otp()
        subject = "OTP for Account Verification"
        body = (f"Thank You For Registering With Us\nYour OTP IS {OTP_.now()}\nOTP VALID FOR 2 MIN\n\nPlease Do Not "
                f"Share This OTP With Anyone")
        from_email = settings.EMAIL_HOST
        to_email = [email]
        rst = send_mail(subject, body, from_email, to_email, fail_silently=False)
        if rst:
            return OTP_.secret
        return False

    def verify_cnf_otp(self, otp, secret, interval=120, digits=4):
        if not otp or not secret:
            return False
        totp = pyotp.totp.TOTP(secret, interval=interval, digits=digits)
        return totp.verify(str(otp))


class Forgot_Password_cnf:
    def send_cnf(self, requests, user):
        token = PasswordResetTokenGenerator()
        id2 = token.make_token(user)
        id1 = urlsafe_base64_encode(force_bytes(user.Email))

        url = requests.build_absolute_uri(reverse('resetpasswordpage', args=[id1, id2]))

        data = {
            'name': user.First_Name + ' ' + user.Last_Name if user.Last_Name else user.First_Name,
            'link': url,
        }

        subject = "Forgot Your Password?"
        body = render_to_string('Core/forgot_password_body.html', data)

        from_email = settings.EMAIL_HOST
        to_email = [user.Email]
        rst = send_mail(subject, '', from_email, to_email, fail_silently=False, html_message=body)
        if rst:
            return True
        return False

    def verify_cnf(self, id1, id2):
        try:
            email = urlsafe_base64_decode(force_str(id1)).decode()
            user = User.objects.get(Email=email)
            token = PasswordResetTokenGenerator()
            if token.check_token(user, id2):
                return user
            return False
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return False
