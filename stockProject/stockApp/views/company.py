from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from stockApp.models import Company, Stock
from rest_framework import status
import random
from datetime import datetime
import uuid

from stockApp.serializers import CompanySerializer, StockRateSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def companies(request):
    companies = Company.objects.all()
    serializer = CompanySerializer(companies, many=True)
    data = serializer.data
    response_data = dict(data)
    response_data = list(data)
    response_data.append({'request_id': str(uuid.uuid4())})
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createCompany(request):
    serializer = CompanySerializer(data=request.data)
    if serializer.is_valid():
        name = serializer.validated_data.get('name')
        if Company.objects.filter(name=name).exists():
            return Response({'error': 'Company with this name already exists.'}, status=status.HTTP_401_BAD_REQUEST)
        company = serializer.save()
        stock_rate_data = {
            'actual': True,
            'rate': random.uniform(5.0, 100.0),
            'date_inc': datetime.now(),
            'company': company.pk  # lub company.pk
        }
        stock_rate_serializer = StockRateSerializer(data=stock_rate_data)
        if stock_rate_serializer.is_valid():
            stock_rate_serializer.save()
            Stock.objects.create(amount=10000, user = request.user, company=company)
            request_id = str(uuid.uuid4())
            return Response({'message': 'Company created successfully.', 'request_id':request_id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
