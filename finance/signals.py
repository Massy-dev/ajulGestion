from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MembershipPayment, Transaction, Category

@receiver(post_save, sender=MembershipPayment)
def create_transaction_on_payment(sender, instance, created, **kwargs):
    if created:
        # On récupère la catégorie "Cotisation"
        category, _ = Category.objects.get_or_create(name="Cotisation", type="income")

        # Crée la transaction
        Transaction.objects.create(
            type="income",
            amount=instance.amount,
            category=category,
            description=f"Cotisation {instance.month}/{instance.year} - {instance.member}",
            member=instance.member,
            date=instance.payment_date,
            created_by=instance.member.user if hasattr(instance.member, "user") else None
        )
