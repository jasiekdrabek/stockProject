import datetime
from rest_framework import serializers
from rest_framework import serializers
from stockApp.models import SellOffer, Stock, StockRate
import random

class SellOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellOffer
        fields = ['company', 'startAmount', 'amount']
        # Usuwamy pole 'user', 'stock', 'dateLimit', 'actual' oraz 'minPrice', bo będą dodawane automatycznie

    def create(self, validated_data):
        request = self.context.get('request')
        company = validated_data['company']
        amount = validated_data['amount']

        # Pobierz najnowszą wartość akcji firmy
        try:
            latest_stock_rate = StockRate.objects.filter(company=company, actual=True).latest('date_inc')
            current_rate = latest_stock_rate.rate
        except StockRate.DoesNotExist:
            raise serializers.ValidationError("No stock rate available for the selected company.")
        
        # Sprawdzanie, czy użytkownik ma wystarczającą ilość akcji
        try:
            stock = Stock.objects.get(user=request.user, company=company)
            if stock.amount < amount:
                raise serializers.ValidationError("You do not have enough shares.")
        except Stock.DoesNotExist:
            raise serializers.ValidationError("You do not own shares of this company.")

        # Ustal cenę w zakresie od 90% do 105% wartości akcji
        min_price = 0.9 * current_rate
        max_price = 1.05 * current_rate
        calculated_price = round(random.uniform(min_price, max_price), 2)

        # Ustawienie dateLimit na 3 minuty od teraz
        date_limit = datetime.datetime.now() + datetime.timedelta(minutes=3)

        # Tworzenie oferty sprzedaży i aktualizacja ilości akcji
        sell_offer = SellOffer.objects.create(
            user=request.user,
            stock=stock,
            minPrice=calculated_price,
            dateLimit=date_limit,
            actual = True,
            **validated_data
        )
        stock.amount -= amount
        stock.save()
        return sell_offer