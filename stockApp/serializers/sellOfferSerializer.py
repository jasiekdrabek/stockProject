from rest_framework import serializers
from stockApp.models import SellOffer

class SellOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellOffer
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        user = validated_data.pop('user')
        return SellOffer.objects.create(user=user, **validated_data)