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
    data = request.data.copy()  # Kopiowanie danych z requestu
    serializer = BuyOfferSerializer(data=data)  # Przekazywanie danych do serializera
    if serializer.is_valid():
        serializer.save(user=request.user)  # Przekazanie użytkownika do metody save serializera
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Zwracanie błędów walidacji

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buyOffers(request):
    buy_offers = BuyOffer.objects.filter(user=request.user)
    serializer = BuyOfferSerializer(buy_offers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteBuyOffer(request,pk):
    try:
        buy_offer = BuyOffer.objects.get(pk=pk, user=request.user)
    except BuyOffer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    buy_offer.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)