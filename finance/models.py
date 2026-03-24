from django.db import models
from django.conf import settings


class Category(models.Model):
    TYPE_CHOICES = (
        ('income', 'Revenue'),
        ('expense', 'Dépense'),
    )

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_per_member = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TYPE_CHOICES = (
        ('income', 'Revenue'),
        ('expense', 'Dépense'),
    )

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    description = models.TextField(blank=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transactions"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.created_at} - {self.type} - {self.amount}"


class MembershipFee(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="membership_fees"
    )
    amount = models.PositiveIntegerField()
    start_date = models.DateField()
    special = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user} - {self.amount}"

class MembershipPayment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="membership_payments"
    )
    amount = models.PositiveIntegerField()
    payment_date = models.DateField(auto_now_add=True)
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("user", "month", "year")

    def __str__(self):
        return f"{self.user} - {self.month}/{self.year}"
