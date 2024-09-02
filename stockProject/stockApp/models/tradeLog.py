from django.db import models

class TradeLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    application_time = models.FloatField()
    database_time = models.FloatField()
    number_of_sell_offers = models.IntegerField()
    number_of_buy_offers = models.IntegerField()
    company_ids = models.JSONField()
