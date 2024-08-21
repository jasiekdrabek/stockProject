# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from stockApp.serializers import BuyOfferSerializer
from stockApp.models import BuyOffer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addBuyOffer(request):
    serializer = BuyOfferSerializer(data=request.data, context={'request': request})  # Przekazywanie danych do serializera
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Zwracanie błędów walidacji

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buyOffers(request):
    buy_offers = BuyOffer.objects.filter(user=request.user, actual = True)
    serializer = BuyOfferSerializer(buy_offers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteBuyOffer(request,pk):
    try:
        buy_offer = BuyOffer.objects.get(pk=pk, user=request.user)
    except BuyOffer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    # Obliczenie kwoty, którą należy zwrócić do pola moneyAfterTransations
    total_cost = buy_offer.amount * buy_offer.maxPrice

    # Aktualizacja pola moneyAfterTransations użytkownika
    user = request.user
    user.moneyAfterTransations += total_cost
    user.save()

    buy_offer.actual = False
    buy_offer.save()
    return Response(status=status.HTTP_204_NO_CONTENT)