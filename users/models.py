from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    
    GENDER_CHOICES = (
        ('male', 'M'),
        ('female', 'F'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
   
    email = models.EmailField(blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    join_date = models.DateField(auto_now_add=True)

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

    USERNAME_FIELD = 'username'  # nom d’utilisateur pour l’authentification
    class Meta:
        ordering = ["join_date"]
    def __str__(self):
        return f"{self.username} {self.last_name}"
    #REQUIRED_FIELDS = ['username']  # nom d’utilisateur requis
