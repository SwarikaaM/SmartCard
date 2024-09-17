from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
import base64
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from functools import partial
from .manager import CustomUserManager
from cryptography.fernet import Fernet
from django.core.files.base import ContentFile


class User_Document(models.Model):
    def rename_document(instance, filename_, base_dir, filename):
        base = Path(base_dir)
        ext = filename_.split('.')[-1]
        folder_name = (
                          instance.User.First_Name + ' ' + instance.User.Last_Name if instance.User.Last_Name else instance.User.First_Name) + '_' + instance.User.Phone_Number
        path = base.joinpath(folder_name).joinpath(filename + '.' + ext)
        return path

    class Meta:
        verbose_name = "User Document"
        verbose_name_plural = "User Documents"

    User = models.ForeignKey('Core.User', on_delete=models.CASCADE)
    Aadhar_Card = models.FileField(
        upload_to=partial(rename_document, base_dir="User Documents", filename='Aadhar Card'))
    Pan_Card = models.FileField(upload_to=partial(rename_document, base_dir="User Documents", filename='Pan Card'))
    Document_Passcode = models.BinaryField(max_length=64, blank=True, editable=False, default=Fernet.generate_key)

    def __str__(self):
        return self.User.First_Name + ' ' + self.User.Last_Name if self.User.Last_Name else self.User.First_Name

    def _encrypt_file(self, file, key=None):
        if key is None:
            key = self.Document_Passcode
        cipher_suite = Fernet(key)
        with open(file.path, "rb") as f:
            encrypted_file = cipher_suite.encrypt(f.read())
        return ContentFile(encrypted_file)

    def _decrypt_file(self, file, key=None):
        if key is None:
            raise ValidationError("Passcode is required to decrypt the file")
            # key = self.Document_Passcode
            # or
            # key = input("Enter the passcode: ").encode()
        cipher_suite = Fernet(key)
        with open(file.path, "rb") as f:
            encrypted_content = f.read()
        decrypted_content = cipher_suite.decrypt(encrypted_content)
        raw = ContentFile(decrypted_content, name=file.name)
        raw_img_code = base64.b64encode(raw.read()).decode('utf-8')
        return raw_img_code

    def get_documents(self):
        return {
            'Aadhar Card': self._decrypt_file(self.Aadhar_Card),
            'Pan Card': self._decrypt_file(self.Pan_Card)
        }


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    RFID = models.CharField(max_length=50, blank=True, unique=True, null=True)
    First_Name = models.CharField(max_length=50)
    Last_Name = models.CharField(max_length=50, blank=True)
    Email = models.EmailField(_("Email Address"), unique=True)
    Phone_Number = models.CharField(max_length=10, unique=True)
    Documents = models.ForeignKey(User_Document, on_delete=models.CASCADE, blank=True, null=True)

    document_choices = ['ACCEPTED', 'REJECTED', 'PENDING', 'NOT SUBMITTED']
    Document_Status = models.CharField(max_length=20, choices=zip(document_choices, document_choices),
                                       default='NOT SUBMITTED')
    Rejection_Reason = models.TextField(blank=True)

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    is_superuser = models.BooleanField(_('superuser status'), default=False,
                                       help_text=_('Designates that this user has all permissions without '
                                                   'explicitly assigning them.'))

    USERNAME_FIELD = "Email"
    REQUIRED_FIELDS = ["First_Name", "Phone_Number"]

    objects = CustomUserManager()

    def __str__(self):
        return self.Email

    def save(self, *args, **kwargs):
        if self.RFID:
            existing_user = User.objects.filter(RFID=self.RFID).exclude(pk=self.pk).first()
            if existing_user:
                raise ValidationError(f"A user with RFID '{self.RFID}' already exists.")

        if self.Document_Status == 'REJECTED':
            if self.Rejection_Reason.strip() == '':
                raise ValidationError("Rejection Reason is required")
            if self.Documents:  # Ensure the Documents field is not None
                self.Documents.Aadhar_Card.delete(save=False)
                self.Documents.Pan_Card.delete(save=False)
                self.Documents.delete()
            self.Documents = None
        elif self.Document_Status == 'ACCEPTED':
            if self.Documents:
                # Encrypt Aadhar_Card and save it back to the FileField
                encrypted_aadhar = self.Documents._encrypt_file(self.Documents.Aadhar_Card)
                self.Documents.Aadhar_Card.save(
                    self.Documents.Aadhar_Card.name,  # Keep the original name
                    encrypted_aadhar,
                    save=False  # Avoid saving the entire model here
                )

                # Encrypt Pan_Card and save it back to the FileField
                encrypted_pan = self.Documents._encrypt_file(self.Documents.Pan_Card)
                self.Documents.Pan_Card.save(
                    self.Documents.Pan_Card.name,  # Keep the original name
                    encrypted_pan,
                    save=False  # Avoid saving the entire model here
                )
                self.Documents.save()
            self.Rejection_Reason = ''
        super().save(*args, **kwargs)
