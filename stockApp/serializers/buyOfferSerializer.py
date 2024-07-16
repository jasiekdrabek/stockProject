from rest_framework import serializers
from stockApp.models import BuyOffer

class BuyOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyOffer
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        user = validated_data.pop('user')
        return BuyOffer.objects.create(user=user, **validated_data)