from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from stockApp.models import Company, Stock, BalanceUpdate, BuyOffer, SellOffer, CustomUser,Transaction, StockRate

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def deleteAllDb(request):
    admin_users = CustomUser.objects.filter(is_superuser=True)

    # Usuwamy wszystkie dane z bazy danych poza adminami
    BuyOffer.objects.all().delete()
    SellOffer.objects.all().delete()
    Stock.objects.all().delete()
    Company.objects.all().delete()
    BalanceUpdate.objects.all().delete()
    Transaction.objects.all().delete()
    StockRate.objects.all().delete()
    # Usuwamy wszystkich użytkowników, którzy nie są adminami
    CustomUser.objects.exclude(id__in=admin_users.values_list('id', flat=True)).delete()

    return Response({"message": "All non-admin data has been deleted."}, status=200)