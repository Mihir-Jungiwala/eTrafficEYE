import os
import uuid

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models


def unique_upload_path(folder):
    def wrapper(instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        return f"{folder}/{uuid.uuid4().hex}{ext}"
    return wrapper


image_validator = FileExtensionValidator(
    allowed_extensions=[
        "jpg",
        "jpeg",
        "png",
        "webp",
    ]
)


class Evidence(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    complaint_no = models.CharField(max_length=50, unique=True)
    complaint_seq = models.IntegerField(unique=True)

    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100)

    datetime = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField()

    violations = models.CharField(max_length=50)

    image1 = models.ImageField(
        upload_to=unique_upload_path("evidence"),
        validators=[image_validator],
        blank=True,
        null=True
    )

    image2 = models.ImageField(
        upload_to=unique_upload_path("evidence"),
        validators=[image_validator],
        blank=True,
        null=True
    )

    image3 = models.ImageField(
        upload_to=unique_upload_path("evidence"),
        validators=[image_validator],
        blank=True,
        null=True
    )

    def __str__(self):
        return self.complaint_no

    # Delete images when object is deleted
    def delete(self, *args, **kwargs):
        if self.image1:
            self.image1.delete(save=False)

        if self.image2:
            self.image2.delete(save=False)

        if self.image3:
            self.image3.delete(save=False)

        super().delete(*args, **kwargs)

    # Delete old images when replaced
    def save(self, *args, **kwargs):

        if self.pk:
            old = Evidence.objects.filter(pk=self.pk).first()

            if old:

                if old.image1 and old.image1 != self.image1:
                    old.image1.delete(save=False)

                if old.image2 and old.image2 != self.image2:
                    old.image2.delete(save=False)

                if old.image3 and old.image3 != self.image3:
                    old.image3.delete(save=False)

        super().save(*args, **kwargs)