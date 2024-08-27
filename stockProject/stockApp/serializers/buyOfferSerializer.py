import datetime
import random
from rest_framework import serializers
from stockApp.models import BuyOffer, StockRate, BalanceUpdate

class BuyOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyOffer
        fields = ['company', 'startAmount', 'amount']
        # Usuwamy pole 'user', 'actual', 'dateLimit' i 'maxPrice', bo będą dodawane automatycznie

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        amount = validated_data['amount']
        company = validated_data['company']
       
        # Pobierz najnowszą wartość akcji firmy
        try:
            latest_stock_rate = StockRate.objects.filter(company=company, actual=True).latest('date_inc')
            current_rate = latest_stock_rate.rate
        except StockRate.DoesNotExist:
            print("add offer stock error")
            raise serializers.ValidationError("No stock rate available for the selected company.")

        # Ustal cenę w zakresie od 95% do 110% wartości akcji
        min_price = 0.95 * current_rate
        max_price = 1.1 * current_rate
        calculated_price = round(random.uniform(min_price, max_price), 2)

        # Sprawdzanie, czy użytkownik ma wystarczającą ilość pieniędzy po uwzględnieniu transakcji
        total_cost = calculated_price * amount
        if user.moneyAfterTransations < total_cost:
            print('buy offer money error')
            raise serializers.ValidationError("You do not have enough money to cover this transaction.")

        # Aktualizacja pola moneyAfterTransations
        BalanceUpdate.objects.create(
            user = user,
            change_amount = -total_cost,
            change_type = 'moneyAfterTransactions',
        )
        # Ustawienie dateLimit na 3 minuty od teraz
        date_limit = datetime.datetime.now() + datetime.timedelta(minutes=3)

        # Tworzenie oferty kupna
        buy_offer = BuyOffer.objects.create(
            user=request.user,
            actual=True,
            maxPrice= calculated_price,
            dateLimit = date_limit,
            **validated_data
        )
        return buy_offer