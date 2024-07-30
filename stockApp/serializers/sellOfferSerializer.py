from rest_framework import serializers
from rest_framework import serializers
from stockApp.models import SellOffer, Stock, Company

class SellOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellOffer
        fields = ['company', 'minPrice', 'startAmount', 'amount', 'dateLimit', 'actual']
        # Usuwamy pole 'user' i 'stock', bo będą dodawane automatycznie

    def create(self, validated_data):
        request = self.context.get('request')
        company = validated_data['company']
        amount = validated_data['amount']

        # Sprawdzanie, czy użytkownik ma wystarczającą ilość akcji
        try:
            stock = Stock.objects.get(user=request.user, company=company)
            if stock.amount < amount:
                raise serializers.ValidationError("You do not have enough shares.")
        except Stock.DoesNotExist:
            raise serializers.ValidationError("You do not own shares of this company.")

        # Tworzenie oferty sprzedaży i aktualizacja ilości akcji
        sell_offer = SellOffer.objects.create(
            user=request.user,
            stock=stock,
            **validated_data
        )
        return sell_offer