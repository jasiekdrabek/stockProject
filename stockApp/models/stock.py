from django.db import models
from .company import Company
from .user import CustomUser

class Stock(models.Model):
    money = models.IntegerField(default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)