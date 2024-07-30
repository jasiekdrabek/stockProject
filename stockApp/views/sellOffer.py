# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from stockApp.serializers import SellOfferSerializer
from stockApp.models import SellOffer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addSellOffer(request):
    serializer = SellOfferSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sellOffers(request):
    sell_offers = SellOffer.objects.filter(user=request.user)
    serializer = SellOfferSerializer(sell_offers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteSellOffer(request,pk):
    try:
        sell_offer = SellOffer.objects.get(pk=pk, user=request.user)
        print(sell_offer)
    except SellOffer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    sell_offer.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)