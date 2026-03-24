from rest_framework import serializers
from .models import CustomUser, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        write_only=True
    )

    role_detail = RoleSerializer(source="role", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "phone",
            "username",
            "last_name",
            "role",
            "photo",
            "role_detail",
            
        ]

   
class UserCreateSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "last_name",
            "phone",
            "role",
            "password",
            "photo",
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user