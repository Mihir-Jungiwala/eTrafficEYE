import os
import uuid

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models


def unique_upload_path(folder):
    def wrapper(instance, filename):
        ext = os.path.splitext(filename)[1]
        return f"{folder}/{uuid.uuid4().hex}{ext}"
    return wrapper


image_validator = FileExtensionValidator(
    allowed_extensions=[
        "jpg",
        "jpeg",
        "png",
        "webp",
        "gif",
        "bmp",
        "tiff",
    ]
)


class Authentication(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='authentication')

    role = models.CharField(max_length=20)

    full_name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15, unique=True)

    # Profile Image
    profile_image = models.ImageField(
        upload_to=unique_upload_path('profile'),
        validators=[image_validator],
        null=True,
        blank=True
    )

    status = models.BooleanField(default=True)

    # Civilian
    civilian_id_card_name = models.CharField(max_length=100, null=True, blank=True)

    # Police
    police_id_number = models.CharField(max_length=100, null=True, blank=True, unique=True)

    # ID Images
    id_image_front = models.ImageField(
        upload_to=unique_upload_path('id'),
        validators=[image_validator],
        null=True,
        blank=True
    )

    id_image_back = models.ImageField(
        upload_to=unique_upload_path('id'),
        validators=[image_validator],
        null=True,
        blank=True
    )

    def __str__(self):
        return self.full_name