import datetime
from rest_framework import serializers
from rest_framework import serializers
from stockApp.models import SellOffer, Stock, StockRate
import random

class SellOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellOffer
        fields = ['company', 'startAmount', 'amount']
    def create(self, validatedData):
        request = self.context.get('request')
        company = validatedData['company']
        amount = validatedData['amount']
        try:
            latestStockRate = StockRate.objects.filter(company=company, actual=True).latest('date_inc')
            currentRate = latestStockRate.rate
        except StockRate.DoesNotExist:
            raise serializers.ValidationError("No stock rate available for the selected company.")
        try:
            stock = Stock.objects.get(user=request.user, company=company)
            if stock.amount < amount:
                raise serializers.ValidationError("You do not have enough shares.")
        except Stock.DoesNotExist:
            raise serializers.ValidationError("You do not own shares of this company.")
        minprice = 0.9 * currentRate
        maxprice = 1.05 * currentRate
        calculatedprice = round(random.uniform(minprice, maxprice), 2)
        dateLimit = datetime.datetime.now() + datetime.timedelta(minutes=3)
        sellOffer = SellOffer.objects.create(
            user=request.user,
            stock=stock,
            minPrice=calculatedprice,
            dateLimit=dateLimit,
            actual = True,
            **validatedData
        )
        stock.amount -= amount
        stock.save()
        return sellOffer