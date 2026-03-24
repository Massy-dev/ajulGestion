#from requests import Response
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.viewsets import ModelViewSet
from twilio.base import serialize
from .models import CustomUser, Role
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    RoleSerializer,
)




class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all().order_by("-join_date")
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def user_me(self, request):
        serializer = UserSerializer(CustomUser.objects.get(id=request.user.id))
        return Response(serializer.data)
        

class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_role(self, request):
        queryset = RoleSerializer(request.user.role)
        return Response(queryset.data)

