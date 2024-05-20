# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from stockApp.serializers import BuyOfferSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addBuyOffer(request):
    data = request.data.copy()  # Kopiowanie danych z requestu
    serializer = BuyOfferSerializer(data=data)  # Przekazywanie danych do serializera
    if serializer.is_valid():
        serializer.save(user=request.user)  # Przekazanie użytkownika do metody save serializera
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Zwracanie błędów walidacji
