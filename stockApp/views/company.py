from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from stockApp.models import Company
from rest_framework import status

from stockApp.serializers import CompanySerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def companies(request):
    companies = Company.objects.all()
    serializer = CompanySerializer(companies, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createCompany(request):
    serializer = CompanySerializer(data=request.data)
    if serializer.is_valid():
        name = serializer.validated_data.get('name')
        if Company.objects.filter(name=name).exists():
            return Response({'error': 'Company with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'message': 'Company created successfully.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
