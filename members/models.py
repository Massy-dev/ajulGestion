from django.db import models
from django.conf import settings

class Member(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="member"
    )
    GENDER_CHOICES = (
        ('male', 'M'),
        ('female', 'F'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    join_date = models.DateField(auto_now_add=True)

    active = models.BooleanField(default=True)
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    photo = models.ImageField(upload_to='members/', blank=True, null=True)
    monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=5000
    )
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
