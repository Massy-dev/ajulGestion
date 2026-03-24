from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path
router = DefaultRouter()
router.register("users", UserViewSet)
router.register("roles", RoleViewSet)

urlpatterns = router.urls
