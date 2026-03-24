from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import *

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("transactions", TransactionViewSet)
router.register("membership-fees/<int:pk>/", MembershipFeeViewSet)
router.register("membership-payments", MembershipPaymentViewSet)

urlpatterns = router.urls

urlpatterns += [
    
    path("finances/dashboard/", DashboardAPIView.as_view()),
    path("stats/monthly/", MonthlyStatsAPIView.as_view()),
    path("members/late/", MembersLateAPIView.as_view()),
    path("members/late/notify/", MembersLateNotifyAPIView.as_view()),
    path("reports/monthly/excel/", MonthlyReportExcelAPIView.as_view()),
    path("reports/monthly/pdf/", MonthlyReportPDFAPIView.as_view()),
    #path("finances/my-payments/", my_payments, name="my-payments"),
]
