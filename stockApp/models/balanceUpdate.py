from django.db import models
from .user import CustomUser

class BalanceUpdate(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    change_amount = models.FloatField()
    change_type = models.CharField(max_length=40, choices=[('money', 'Money'), ('moneyAfterTransactions', 'Money After Transactions')])
    created_at = models.DateTimeField(auto_now_add=True)
    actual = models.BooleanField(default=True)
