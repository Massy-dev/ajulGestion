from rest_framework.viewsets import ModelViewSet
from .models import Member
from .serializers import MemberSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action

class MemberViewSet(ModelViewSet):
    queryset = Member.objects.all().order_by("-id")
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]  # only authenticated users can view members
    def get_queryset(self):
        return Member.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    def perform_destroy(self, instance):
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def my_profile(self, request):
        member = request.user
        serializer = MemberSerializer(member)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def members_in_debt(self, request):
        members = Member.objects.filter(balance__gt=0)
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)






