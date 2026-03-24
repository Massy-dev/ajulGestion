from django.contrib.auth.models import User
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum, F
from django.utils.timezone import now
from django.db.models.functions import ExtractMonth, ExtractYear
from .permissions import IsTreasurerOrAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated
from .utils import send_whatsapp_message
from datetime import datetime
from django.http import HttpResponse
import openpyxl
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from rest_framework.decorators import action
from .models import *
from users.models import CustomUser

from .serializers import (
    MembershipFeeSerializer,
    MembershipPaymentSerializer,
)
from .permissions import IsTreasurerOrAdmin
from rest_framework import status
from .models import Category, Transaction
from .serializers import (
    CategorySerializer,
    TransactionSerializer,
)


class CategoryViewSet(ModelViewSet):
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
   

    def perform_create(self, serializer):
        serializer.save()
    


class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.select_related(
        "user","category",
        ).order_by("-created_at")

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user,date=datetime.now())
        print("serializer data transact ", serializer.data)
    
    
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def userPaiment(self, request):
        user_id = self.request.query_params.get("user")
        transact = Transaction.objects.filter(user=user_id)
        serializer = TransactionSerializer(transact, many=True)
        print("User iddddd---",serializer.data)
        return Response(serializer.data)


    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def total(self, request):

        user_id = request.query_params.get("user")
        transact = Transaction.objects.filter(user=user_id)
        serializer = TransactionSerializer(transact, many=True)
        
        #month = request.query_params.get("month")
        #year = request.query_params.get("year")

        #queryset = queryset.filter(user=user_id)

        #if month and year:
        #queryset = queryset.filter(date__month=month, date__year=year)

        total = transact.aggregate(total=Sum("amount"))["total"] or 0
        return Response({
            "total": total,
            "users":"ff"})

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def member(self, request, pk):  
        payments = Transaction.objects.filter(user=pk)
        serializer = TransactionSerializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="stats/categories", permission_classes=[IsAuthenticated])
    def stats_by_category(self, request):

        queryset = Transaction.objects.select_related("category")

        data = (
            queryset
            .values("category__id", "category__name", "category__total_amount")
            .annotate(total=Sum("amount"))
        )

        results = []

        for item in data:
            total_expected = item["category__total_amount"] or 0
            total_paid = item["total"] or 0

            results.append({
                "category": item["category__name"],
                "total_topaid":total_expected,
                "total_paid": total_paid,
                "remaining": total_expected - total_paid,
            })

        return Response(results)
    
    @action(detail=False, methods=["get"], url_path="stats/top-members")
    def top_members(self, request):

        queryset = Transaction.objects.select_related("user")

        data = (
            queryset
            .values(
                "user__id",
                "user__username",
                "user__last_name"
            )
            .annotate(total=Sum("amount"))
            .order_by("-total")[:5]
        )

        results = [
            {
                "name": f"{item['user__username']} {item['user__last_name']}",
                "total": item["total"]
            }
            for item in data
        ]

        return Response(results)

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        today = now().date()
        current_month = today.month
        current_year = today.year
        total_members = CustomUser.objects.count()
        
        transactions = Transaction.objects.all()

        total_income = (
            transactions.filter(type="income")
            .aggregate(total=Sum("amount"))["total"] or 0
        )

        total_expense = (
            transactions.filter(type="expense")
            .aggregate(total=Sum("amount"))["total"] or 0
        )

        monthly_income = (
            transactions.filter(
                #type="income",
                date__month=current_month,
                date__year=current_year,
            ).aggregate(total=Sum("amount"))["total"] or 0
        )

        monthly_expense = (
            transactions.filter(
                type="expense",
                date__month=current_month,
                date__year=current_year,
            ).aggregate(total=Sum("amount"))["total"] or 0
        )

        balance = total_income - total_expense

        return Response({
            "balance": balance,
            "total_income": total_income,
            "total_expense": total_expense,
            "monthly_income": monthly_income,
            "monthly_expense": monthly_expense,
            "transaction_count": transactions.count(),
            "total_members": total_members,
        })

class MonthlyStatsAPIView(APIView):
    def get(self, request):
        transactions = Transaction.objects.all()

        monthly_data = (
            transactions
            .annotate(
                year=ExtractYear("date"),
                month=ExtractMonth("date"),
            )
            .values("year", "month", "type")
            .annotate(total=Sum("amount"))
            .order_by("year", "month")
        )

        result = {}

        for item in monthly_data:
            key = f"{item['year']}-{item['month']:02d}"

            if key not in result:
                result[key] = {
                    "income": 0,
                    "expense": 0,
                }

            result[key][item["type"]] = item["total"]

        # calcul du solde cumulatif
        balance = 0
        response_data = []

        for month, values in result.items():
            balance += values["income"] - values["expense"]

            response_data.append({
                "month": month,
                "income": values["income"],
                "expense": values["expense"],
                "balance": balance,
            })

        return Response(response_data)


class MembershipFeeViewSet(ModelViewSet):
    queryset = MembershipFee.objects.all()
    serializer_class = MembershipFeeSerializer
    permission_classes = [IsTreasurerOrAdmin]
    def get(self, request, pk):
        transaction = Transaction.objects.filter(user=pk)
        serializer = TransactionSerializer(transaction, many=True,ontext={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class MembershipPaymentViewSet(ModelViewSet):
    queryset = MembershipPayment.objects.all()
    serializer_class = MembershipPaymentSerializer
    #permission_classes = [IsTreasurerOrAdmin]
    
    
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def own(self, request):
        member = request.user
        payments = Transaction.objects.filter(user=member)
        serializer = TransactionSerializer(payments, many=True)
        return Response(serializer.data)

class MembersLateAPIView(APIView):
    def get(self, request):
        today = now()
        current_month = today.month
        current_year = today.year

        late_members = []

        for fee in MembershipFee.objects.all():
            paid = MembershipPayment.objects.filter(
                member=fee.member,
                month=current_month,
                year=current_year,
            ).exists()

            if not paid:
                late_members.append({
                    "member_id": fee.member.id,
                    "member_name": str(fee.member),
                    "amount_due": fee.amount,
                })

        return Response(late_members)


class MembersLateNotifyAPIView(APIView):
    permission_classes = [IsTreasurerOrAdmin]

    def post(self, request):
        today = now()
        current_month = today.month
        current_year = today.year

        late_members = []

        for fee in MembershipFee.objects.all():
            paid = MembershipPayment.objects.filter(
                member=fee.member,
                month=current_month,
                year=current_year,
            ).exists()

            if not paid:
                late_members.append(fee.member)
                
                # envoi WhatsApp
                if fee.member.phone:
                    message = f"Bonjour {fee.member.first_name}, vous n'avez pas encore payé votre cotisation pour {current_month}/{current_year}. Merci de régulariser rapidement."
                    send_whatsapp_message(fee.member.phone, message)

        return Response({
            "notified_count": len(late_members),
            "members": [str(m) for m in late_members]
        })


class MonthlyReportExcelAPIView(APIView):
    permission_classes = [IsTreasurerOrAdmin]

    def get(self, request, year=None, month=None):
        # valeurs par défaut : mois courant
        today = datetime.today()
        year = year or today.year
        month = month or today.month

        transactions = Transaction.objects.filter(
            date__year=year,
            date__month=month
        )

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename=rapport_{year}_{month}.xlsx'

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Transactions"

        # Header
        ws.append(["Date", "Type", "Montant", "Catégorie", "Membre", "Description"])

        for t in transactions:
            ws.append([
                t.date.strftime("%Y-%m-%d"),
                t.type,
                t.amount,
                t.category.name if t.category else "",
                str(t.member) if t.member else "",
                t.description
            ])

        wb.save(response)
        return response
    

class MonthlyReportPDFAPIView(APIView):

    permission_classes = [IsAuthenticated]
    #permission_classes = [IsTreasurerOrAdmin]

    def get(self, request, year=None, month=None):
        today = datetime.today()
        year = year or today.year
        month = month or today.month

        transactions = Transaction.objects.filter(
            date__year=year,
            date__month=month
        )

        balance = sum(
            t.amount if t.type == "income" else -t.amount
            for t in transactions
        )

        html = render_to_string(
            "finance/monthly_report.html",
            {
                "transactions": transactions,
                "month": month,
                "year": year,
                "balance": balance
            }
        )

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if pdf.err:
            return HttpResponse("Erreur lors de la génération du PDF", status=500)

        response = HttpResponse(result.getvalue(), content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename=rapport_{year}_{month}.pdf'
        return response
        


