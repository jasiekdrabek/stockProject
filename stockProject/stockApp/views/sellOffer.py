# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from stockApp.serializers import SellOfferSerializer
from stockApp.models import SellOffer, Stock
import uuid

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addSellOffer(request):
    serializer = SellOfferSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        data = serializer.data
        response_data = dict(data)
        response_data['request_id'] = str(uuid.uuid4())
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sellOffers(request):
    sell_offers = SellOffer.objects.filter(user=request.user, actual = True)
    serializer = SellOfferSerializer(sell_offers, many=True)
    data = serializer.data
    response_data = list(data)
    response_data.append({'request_id': str(uuid.uuid4())})
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteSellOffer(request, pk):
    try:
        # Pobranie oferty sprzedaży dla zalogowanego użytkownika
        sell_offer = SellOffer.objects.get(pk=pk, user=request.user)
    except SellOffer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Zwrócenie akcji użytkownikowi
    try:
        stock = Stock.objects.get(user=request.user, company=sell_offer.company)
        stock.amount += sell_offer.amount  # Przywrócenie akcji
        stock.save()
    except Stock.DoesNotExist:
        # Jeśli użytkownik nie ma akcji w tej firmie, stworzymy nowy rekord w Stock
        Stock.objects.create(user=request.user, company=sell_offer.company, amount=sell_offer.amount)

    # Usunięcie oferty sprzedaży
    sell_offer.actual = False
    sell_offer.save()
    return Response({'request_id': str(uuid.uuid4())},status=status.HTTP_204_NO_CONTENT)