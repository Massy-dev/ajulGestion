from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path

router = DefaultRouter()
router.register("members", MemberViewSet)

urlpatterns = router.urls


"""urlpatterns += [
    path("members/in-debt/", members_in_debt, name="members-in-debt"),
    path("members/me/", my_profile, name="my-profile"),
]"""