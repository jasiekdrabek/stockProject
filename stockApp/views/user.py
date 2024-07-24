from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from stockApp.serializers import UserUpdateSerializer
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