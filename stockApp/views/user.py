from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from stockApp.serializers import UserUpdateSerializer, StockSerializer, CustomUserInfoSerializer
from stockApp.models import Stock, CustomUser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def addMoney(request):
    user = request.user
    serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserStocks(request):
    stocks= Stock.objects.filter(user=request.user)
    serializer = StockSerializer(stocks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserInfo(request):
    user = request.user
    serializer = CustomUserInfoSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)