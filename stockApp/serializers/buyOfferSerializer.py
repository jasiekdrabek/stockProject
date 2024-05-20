from rest_framework import serializers
from stockApp.models import BuyOffer

class BuyOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyOffer
        fields = '__all__'
        read_only_fields = ['user']