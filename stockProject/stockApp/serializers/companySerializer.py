from rest_framework import serializers
from stockApp.models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

        def create(self, validatedData):
            company = Company(
                name = validatedData['name'],
                )
            company.save()
            return company