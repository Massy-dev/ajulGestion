from datetime import datetime
from rest_framework import serializers
from .models import Category, Transaction
from users.models import CustomUser
from .models import MembershipFee, MembershipPayment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "total_amount",
            "amount_per_member",
        ]


class TransactionSerializer(serializers.ModelSerializer):

    # écriture
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        write_only=True
    )

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True
    )

    # lecture
    user_detail = serializers.SerializerMethodField(read_only=True)
    category_detail = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y", read_only=True)
    class Meta:
        model = Transaction
        fields = [
            "id",
            "amount",
            "description",
            "user",
            "category",
            "user_detail",
            "category_detail",
            "created_at",
        ]

    def get_user_detail(self, obj):
        if obj.user:
            return {
                "id": obj.user.id,
                "username": obj.user.username,
                "last_name": obj.user.last_name,
                "phone": obj.user.phone
            }
        return None

    def get_category_detail(self, obj):
        if obj.category:
            return {
                "id": obj.category.id,
                "name": obj.category.name,
                "amount_per_member": obj.category.amount_per_member
            }
        return None


class MembershipFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipFee
        fields = "__all__"


class MembershipPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"

        def create(self, validated_data):
            payment = Transaction.objects.create(**validated_data)

            member = payment.member
            member.balance -= payment.amount
            member.save()

            return payment
